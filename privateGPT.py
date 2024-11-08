from langchain.chains import RetrievalQA
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.vectorstores import Chroma
from langchain.llms import Ollama
import os
import argparse
import time

# Configuration
model = os.environ.get("MODEL", "mistral")
embeddings_model_name = os.environ.get("EMBEDDINGS_MODEL_NAME", "all-MiniLM-L6-v2")
persist_directory = os.environ.get("PERSIST_DIRECTORY", "db")
target_source_chunks = int(os.environ.get('TARGET_SOURCE_CHUNKS', 4))

CHROMA_SETTINGS = {
    "host": "localhost",
    "port": 8000,
    "persist_directory": "./chroma_data",
    "metric": "cosine",
    "embedding_dim": 768
}

def get_answer(query, hide_source=False, mute_stream=False):
    """
    Fetches an answer for the given query using the configured LLM and Chroma database.

    :param query: The query to ask the LLM.
    :param hide_source: If True, do not include source documents in the response.
    :param mute_stream: If True, suppress streaming output.
    :return: A tuple containing the answer and a list of source documents.
    """
    embeddings = HuggingFaceEmbeddings(model_name=embeddings_model_name)
    db = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
    retriever = db.as_retriever(search_kwargs={"k": target_source_chunks})
    
    # Set up callbacks for streaming output
    callbacks = [] if mute_stream else [StreamingStdOutCallbackHandler()]
    llm = Ollama(model=model, callbacks=callbacks)
    
    qa = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever, return_source_documents=not hide_source)
    res = qa(query)
    
    answer = res['result']
    docs = [] if hide_source else res['source_documents']
    return answer #, docs

def main():
    # Parse command line arguments
    args = parse_arguments()
    while True:
        query = input("\nEnter a query: ")
        if query == "exit":
            break
        if query.strip() == "":
            continue

        # Get the answer
        start = time.time()
        answer, docs = get_answer(query, hide_source=args.hide_source, mute_stream=args.mute_stream)
        end = time.time()

        # Print the result
        print("\n\n> Question:")
        print(query)
        print(answer)

        # Print the relevant sources used for the answer
        if not args.hide_source:
            for document in docs:
                print("\n> " + document.metadata["source"] + ":")
                print(document.page_content)

def parse_arguments():
    parser = argparse.ArgumentParser(description='privateGPT: Ask questions to your documents without an internet connection, '
                                                 'using the power of LLMs.')
    parser.add_argument("--hide-source", "-S", action='store_true',
                        help='Use this flag to disable printing of source documents used for answers.')
    parser.add_argument("--mute-stream", "-M",
                        action='store_true',
                        help='Use this flag to disable the streaming StdOut callback for LLMs.')

    return parser.parse_args()

if __name__ == "__main__":
    main()
