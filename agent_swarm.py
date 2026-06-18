import httpx

class AgentSwarm:
    def __init__(self, ollama_url="http://127.0.0.1:11434/api/chat"):
        self.url = ollama_url
        self.model = "llama3.2:1b"

    async def _query_local_llm(self, system_prompt, user_content):
        """Asynchronous HTTP call using httpx to prevent thread deadlocks"""
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            "stream": False,
            "options": {"temperature": 0.0}
        }
        try:
            # Use async context manager with an explicit 30s timeout
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(self.url, json=payload)
                return response.json().get("message", {}).get("content", "Inference empty.")
        except Exception as e:
            return f"Failed to reach local Ollama node: {str(e)}"

    async def execute_triage_debate(self, raw_log_text):
        print("🕵️‍♂️ Formulating specialized agent perspectives...")
        
        timing_persona = (
            "You are an expert ASIC Static Timing Analysis (STA) engineer. "
            "Analyze this log snippet strictly looking for clock domain issues, setup/hold violations, "
            "or register synchronization delays. Keep your summary to 2 dense sentences."
        )
        # Await the async network call
        timing_analysis = await self._query_local_llm(timing_persona, raw_log_text)
        print(f"⏱️ [Timing Agent Review]: {timing_analysis}\n")

        rtl_persona = (
            "You are a Principal RTL Design Engineer specializing in protocol verification. "
            "Analyze this log snippet strictly looking for functional logic bugs, state-machine lockups, "
            "infinite recursive software loops, or FIFO overflows. Keep your summary to 2 dense sentences."
        )
        # Await the async network call
        rtl_analysis = await self._query_local_llm(rtl_persona, raw_log_text)
        print(f"💻 [RTL Design Agent Review]: {rtl_analysis}\n")

        orchestrator_persona = (
            "You are the Lead Verification Triage Architect. Review the structural log data alongside the "
            "two independent domain reviews provided by your engineering team. Resolve any conflicts and compile "
            "a final, highly technical Root Cause Analysis detailing: Error Signature, Impacted Component, and Debug Summary."
        )
        
        combined_context = (
            f"Raw Log Data:\n{raw_log_text}\n\n"
            f"Timing Team Input:\n{timing_analysis}\n\n"
            f"RTL Design Team Input:\n{rtl_analysis}"
        )
        
        print("⚖️ Orchestrator synthesizing consensus...")
        final_verdict = await self._query_local_llm(orchestrator_persona, combined_context)
        return final_verdict