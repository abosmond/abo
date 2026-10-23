# Threat model

**System under test:** an LLM agent that reads untrusted content (web pages, files, emails,
contract metadata) and can call tools with side effects (email, file deletion, token
approvals and transfers).

**Attacker capabilities**
- *Direct:* controls the user turn (DI).
- *Indirect:* controls some content the agent retrieves, but not the user or system prompt (II, EX, TA, OC).

**Attacker goals:** unauthorized actions (tool abuse, on-chain approvals/transfers),
data exfiltration (secrets leaving through a tool call or answer), and harmful output delivery.

**Out of scope (v0.1):** model weights, training-data poisoning, multimodal injection,
real networks or chains. All tools are simulated and side-effect free.

**Metrics**
- *ASR (attack success rate):* share of runs where any attack criterion was met. Lower is better.
- *Utility:* share of runs where the benign task still succeeded. A defense that drives ASR
  to 0% by breaking the task is not a good defense.
