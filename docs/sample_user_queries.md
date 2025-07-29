To test our framework effectively, we want to cover different aspects of the **retrieval**, **change suggestion**, and **user interface behavior**. Here's a set of test questions and scenarios that validate the system's ability to:

* Understand intent from natural language
* Retrieve relevant documentation pages
* Suggest meaningful edits
* Handle edge cases

---

## ✅ Core Test Questions for the Framework (Generated using ChatGPT)

### 🔄 *Behavioral Change Detection*

1. **"We no longer use `as_tool`. All agent invocations must go through `handoff`."**

   > ✅ Should retrieve pages where `as_tool` is mentioned and suggest replacing it with `handoff`.

2. **"The `run_agent()` function has been deprecated."**

   > ✅ Should retrieve documentation describing `run_agent()` and mark it as `removed` or `deprecated`.

3. **"We now support function calling using `FunctionTool` instead of `Tool`."**

   > ✅ Should modify descriptions or examples using `Tool` to recommend `FunctionTool`.

---

### 📚 *Content Addition or Enhancement*

4. **"Add an example of how to implement a custom agent handler."**

   > ✅ Should detect a relevant section like `agent.py` or `custom agents` and suggest inserting example code.

5. **"Mention that `ToolParameterSchema` must be defined using Pydantic 2.0 syntax."**

   > ✅ Should find references to `ToolParameterSchema` and update schema definitions or add a warning.

---

### ❌ *Removing or Flagging Outdated Content*

6. **"Remove all references to `MCPTool`, it's no longer supported."**

   > ✅ Should retrieve pages referencing `MCPTool` and mark them for removal.

7. **"Outdated info: agents are no longer auto-dispatched in run loop."**

   > ✅ Should find that claim and update or remove it.

---

### ⚠️ *Ambiguity and Edge Case Handling*

8. **"Fix inaccuracies around agent initialization."**

   > ✅ Should retrieve `agent initialization` sections and try to identify outdated patterns or assumptions.

9. **"We now use the term 'toolchain' instead of 'toolset'."**

   > ✅ Should update all occurrences of `toolset` in meaningful contexts.

---

## 🧪 UI/UX Testing Prompts

Use these to test how the **frontend handles output**:

10. **"Agents now support multithreading."**

> Does it show suggested changes clearly? Is diff view usable?

11. **"Tool output is now JSON, not string."**

> Does the change type show `modified`? Is suggested content shown side-by-side?

12. **"Update examples for OpenAI-compatible agents."**

> Test if frontend can handle long text diffs and allow approving/rejecting them smoothly.

---

## Optional: Stress Test

13. **"Refactor the entire docs to follow the new SDK layout."**

> Should either refuse or give manageable suggestions (not explode).

14. **"Nothing should change."**

> Should return results marked as `unchanged` or nothing at all.
