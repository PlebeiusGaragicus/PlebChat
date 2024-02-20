
        # from langchain_core.messages import HumanMessage
        # inputs = {"messages": [HumanMessage(content=prompt)]}

        # async for output in st.session_state.graph.astream_log(inputs, include_types=["llm"]):
        #     # astream_log() yields the requested logs (here LLMs) in JSONPatch format
        #     for op in output.ops:
        #         print(op)
        #         continue

        #         if op["path"] == "/streamed_output/-":
        #             # this is the output from .stream()
        #             # print(op["value"])
        #             print(op['value'])
        #             # st.session_state.incomplete_stream += op["value"]
        #             # place_holder.markdown(st.session_state.incomplete_stream)

        #         elif op["path"].startswith("/logs/") and op["path"].endswith("/streamed_output/-"):
        #             # because we chose to only include LLMs, these are LLM tokens
        #             print("STREAMING LLM TOKENS!!!!!!!!")
        #             print(op["value"])
        #             # st.session_state.incomplete_stream += op["value"]
        #             # place_holder.markdown(st.session_state.incomplete_stream)

        from langchain_core.messages import HumanMessage
        inputs = {"messages": [HumanMessage(content=prompt)]}
        for output in st.session_state.graph.stream(inputs):
            # stream() yields dictionaries with output keyed by node name
            for key, value in output.items():
                st.session_state.incomplete_stream = f"{key}: {value}"
                place_holder.markdown(st.session_state.incomplete_stream)
                # st.write(f"{key}: {value}")
                print(f"Output from node '{key}':")
                print(value)


        # for chunk in st.session_state.model.get_streamed_tokens(client):
            # st.session_state.incomplete_stream += chunk
            # place_holder.markdown(st.session_state.incomplete_stream)