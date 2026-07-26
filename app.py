"""
Production-ready Knowledge Base Chat Application
Supports both Amazon Knowledge Bases and Amazon Kendra retrievers
Supports both simple Q&A and conversational chains with history
Optional PTO/time off management functionality
"""

import os
from typing import Optional

import streamlit as st
from dotenv import load_dotenv

from langchain.chains import ConversationalRetrievalChain, RetrievalQA
from langchain.chains.conversational_retrieval.prompts import CONDENSE_QUESTION_PROMPT
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_community.llms import Bedrock
from langchain_community.retrievers import AmazonKendraRetriever, AmazonKnowledgeBasesRetriever
from langchain.memory import ConversationBufferMemory
from langchain.prompts.prompt import PromptTemplate
from langchain.tools import Tool
from langchain.agents import initialize_agent, AgentType

# Import PTO manager
from pto_manager import pto_manager

# Load environment variables
load_dotenv()

# Configuration
PAGE_TITLE = os.getenv("PAGE_TITLE", "Knowledge Base Assistant")
APP_TITLE = os.getenv("APP_TITLE", "Knowledge Base Assistant")
DEFAULT_MODEL_ID = os.getenv("MODEL_ID", "anthropic.claude-instant-v1")
RETRIEVER_TYPE = os.getenv("RETRIEVER_TYPE", "knowledge_base")  # Options: "knowledge_base" or "kendra"
CHAIN_TYPE = os.getenv("CHAIN_TYPE", "conversational")  # Options: "conversational" or "simple" or "agent"
ENABLE_PTO = os.getenv("ENABLE_PTO", "false").lower() == "true"
KNOWLEDGE_BASE_ID = os.getenv("KNOWLEDGE_BASE_ID", "")
KENDRA_INDEX_ID = os.getenv("KENDRA_INDEX_ID", "")
TOP_K_RESULTS = int(os.getenv("TOP_K_RESULTS", "4"))

# Model parameters
MODEL_KWARGS = {
    "temperature": float(os.getenv("TEMPERATURE", "0")),
    "top_k": int(os.getenv("TOP_K", "10")),
    "max_tokens_to_sample": int(os.getenv("MAX_TOKENS_TO_SAMPLE", "750")),
}


def get_retriever():
    """Initialize and return the appropriate retriever based on configuration."""
    if RETRIEVER_TYPE == "kendra":
        if not KENDRA_INDEX_ID:
            st.error("KENDRA_INDEX_ID environment variable is required for Kendra retriever")
            st.stop()
        return AmazonKendraRetriever(
            index_id=KENDRA_INDEX_ID,
            top_k=TOP_K_RESULTS,
        )
    else:  # knowledge_base
        if not KNOWLEDGE_BASE_ID:
            st.error("KNOWLEDGE_BASE_ID environment variable is required for Knowledge Base retriever")
            st.stop()
        return AmazonKnowledgeBasesRetriever(
            knowledge_base_id=KNOWLEDGE_BASE_ID,
            retrieval_config={"vectorSearchConfiguration": {"numberOfResults": TOP_K_RESULTS}},
        )


def get_llm():
    """Initialize and return the Bedrock LLM."""
    return Bedrock(model_id=DEFAULT_MODEL_ID, model_kwargs=MODEL_KWARGS)


def get_prompt_template():
    """Create and return the prompt template for the conversational chain."""
    if CHAIN_TYPE == "conversational":
        template = """
Human:
    You are a conversational assistant designed to help answer questions from a knowledge base.
    Use the following pieces of context to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer. Keep the answer as concise as possible.

{context}

{chat_history}

Question: {question}

Assistant:
"""
        return PromptTemplate(
            input_variables=["context", "chat_history", "question"],
            template=template,
        )
    else:  # simple chain
        template = """Use the following pieces of context to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer. Keep the answer as concise as possible.
{context}
Question: {question}
Helpful Answer:"""
        return PromptTemplate.from_template(template)


def get_pto_balance(employee_id: str) -> str:
    """Tool function to get PTO balance for an employee."""
    result = pto_manager.get_pto_balance(employee_id)
    if "error" in result:
        return f"Error: {result['error']}"
    return f"Employee {result['employee_name']} (ID: {result['employee_id']}) has {result['pto_balance']} PTO days remaining."


def request_pto(employee_id: str, pto_days: int) -> str:
    """Tool function to request PTO for an employee."""
    result = pto_manager.request_pto(employee_id, pto_days)
    if "error" in result:
        return f"Error: {result['error']}"
    return f"PTO request approved for {result['employee_name']} (ID: {result['employee_id']}). Requested: {result['pto_requested']} days. Remaining: {result['pto_remaining']} days."


def list_employees() -> str:
    """Tool function to list all employees with PTO balances."""
    result = pto_manager.list_employees()
    output = f"Total employees: {result['total_count']}\n\n"
    for emp in result['employees']:
        output += f"- {emp['employee_name']} (ID: {emp['employee_id']}): {emp['pto_balance']} days\n"
    return output


def get_pto_tools():
    """Create and return PTO tools for the agent."""
    return [
        Tool(
            name="Get PTO Balance",
            func=lambda x: get_pto_balance(x),
            description="Get the PTO balance for an employee. Input should be the employee ID."
        ),
        Tool(
            name="Request PTO",
            func=lambda x: request_pto(x.split(',')[0], int(x.split(',')[1])),
            description="Request PTO for an employee. Input should be 'employee_id,pto_days' (e.g., '123,5')."
        ),
        Tool(
            name="List Employees",
            func=lambda x: list_employees(),
            description="List all employees with their PTO balances. No input needed."
        ),
    ]


def main():
    """Main application entry point."""
    # Configure Streamlit app
    st.set_page_config(
        page_title=PAGE_TITLE,
        page_icon="🤖",
        layout="wide",
    )
    st.title(APP_TITLE)

    # Display configuration info in sidebar
    with st.sidebar:
        st.header("Configuration")
        st.info(f"Retriever Type: {RETRIEVER_TYPE}")
        st.info(f"Chain Type: {CHAIN_TYPE}")
        st.info(f"PTO Enabled: {ENABLE_PTO}")
        st.info(f"Model: {DEFAULT_MODEL_ID}")
        if RETRIEVER_TYPE == "kendra":
            st.info(f"Kendra Index ID: {KENDRA_INDEX_ID or 'Not set'}")
        else:
            st.info(f"Knowledge Base ID: {KNOWLEDGE_BASE_ID or 'Not set'}")
        st.info(f"Top K Results: {TOP_K_RESULTS}")

    # Initialize components
    try:
        retriever = get_retriever()
        llm = get_llm()
        prompt_template = get_prompt_template()
    except Exception as e:
        st.error(f"Error initializing components: {str(e)}")
        st.stop()

    # Set up message history
    msgs = StreamlitChatMessageHistory(key="langchain_messages")
    
    if CHAIN_TYPE == "conversational":
        memory = ConversationBufferMemory(
            chat_memory=msgs,
            memory_key="chat_history",
            output_key="answer",
            return_messages=True,
        )
    else:  # simple chain
        memory = ConversationBufferMemory(
            chat_memory=msgs,
            memory_key="history",
            ai_prefix="Assistant",
            output_key="answer",
        )

    # Add initial greeting if no messages
    if len(msgs.messages) == 0:
        msgs.add_ai_message("How can I help you today?")

    # Configure the chain based on chain type
    if CHAIN_TYPE == "agent":
        if not ENABLE_PTO:
            st.error("PTO must be enabled for agent chain type")
            st.stop()
        
        tools = get_pto_tools()
        agent = initialize_agent(
            tools=tools,
            llm=llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            memory=memory,
        )
        qa = agent
    elif CHAIN_TYPE == "conversational":
        qa = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=retriever,
            return_source_documents=True,
            combine_docs_chain_kwargs={"prompt": prompt_template},
            memory=memory,
            condense_question_prompt=CONDENSE_QUESTION_PROMPT,
        )
    else:  # simple chain
        qa = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True,
            chain_type_kwargs={"prompt": prompt_template},
        )

    # Render current messages from StreamlitChatMessageHistory
    for msg in msgs.messages:
        st.chat_message(msg.type).write(msg.content)

    # Handle user input
    if prompt := st.chat_input("Ask a question..."):
        st.chat_message("human").write(prompt)

        try:
            # Invoke the model based on chain type
            with st.spinner("Thinking..."):
                if CHAIN_TYPE == "agent":
                    output = qa.invoke({"input": prompt})
                    answer = output["output"]
                elif CHAIN_TYPE == "conversational":
                    output = qa.invoke(
                        {"question": prompt, "chat_history": memory.load_memory_variables({})}
                    )
                    answer = output["answer"]
                else:  # simple chain
                    output = qa.invoke({"query": prompt})
                    answer = output["result"]
                    # Add messages to memory for simple chain
                    memory.chat_memory.add_user_message(prompt)
                    memory.chat_memory.add_ai_message(answer)

            # Display the output
            st.chat_message("ai").write(answer)

            # Optionally display source documents (only for retrieval chains)
            if CHAIN_TYPE != "agent" and st.checkbox("Show source documents"):
                with st.expander("Source Documents"):
                    for i, doc in enumerate(output["source_documents"], 1):
                        st.write(f"**Source {i}:**")
                        st.write(doc.page_content)
                        st.write("---")

        except Exception as e:
            st.error(f"Error generating response: {str(e)}")


if __name__ == "__main__":
    main()
