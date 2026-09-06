1. have terminal icons have way to back default if dont have nerd fonts
2. having claude codes background agent concept (namely one that is fork and inherets context and how does that? also how do these background agents communicate with current agent)
3. have claude code reseearch different spec structures so could start to add (look at prompt_toolkit fork that maitnaines spec)
    1. skill file that helps write spec (and helps make sure context window not too large)
4. have formal rfc folder process (that will use similar attributes used before, eg if accepted or not). allowing me to give manual overview
5. have copy like icon to copy code boxes (see github copliots chat)
6. have app that allows to install skills and keep up to date (for example the spec skill likely want to use across my different repos)
7. update agents coding capabilities to ensure agent has proper context as designs. for example leaving comments for non-intuitive code changes (ones that need to know the why, with some examples?)
    1. in general should look at some prompting best practices, and guides
8. having AI add tests as go (or at least easy way to log test cases so after prototyping we can go back and add them, as want some integration and specific scenario tests, for integration/e2e be cool if way can record as do session)
9. add org ideas (like tickets, spec, rfcs, etc) that allow me to be overview approving and giving arch guidance & PR like guidance but not as much as actual code writing (what things would i write up, want specifyied by my team and communicate with)
    10. as description of what makes good dev (eg what qualities, short and to point, gives own options along with ones i ask, ask clarifying questions, etc - basically what characteristics/habits/practices want my team dev to have with me)
10. ensure python mode is using uv
11. ability to choose themes
12. think of how can make the AI thinking more explicit, or ability to dig in (this part like about github copilot a lot, as bit mysterious what claude is doing, and i dont get to learn along the way because of it)
13. understand how claude makes inferences like " I'd rule it out for the same reason ty was ruled out (when looking at adding sqls, go based)", is that claude ai model, or claude code helping have that type of inference
14. ability to add quick todo (and ways to see if make todo's into tickets)
15. see if use https://pypi.org/project/textual-autocomplete/ (this one has built in filepath completion, color highlighting, up date to case of suggestion) or built in suggester
16. see if part of design research items have dbeaver to be what capabilities modeled after
17. way to research so dont re-invent wheel, like when made own completion widget we should have looked at what extensions out there (where can look, what determines if good project - eg is it abandoned or not, etc)
18. have as practice that if catch bug it adds automated test for (even in POC, perhaps just in POC decide what checks you are runnign through each session, though seems like claude does some e2e test anyways). have template of the docstring of the test so know the why and acceptance criteria it is helping with
19. note: may be hard to do all of claude code in this TUI but having it be an agentic scripting tool is really helpful
20. ability to copy and add all mode cells to clipboard or to .py or .sql file
21. have some look at performance (eg is way does autocomplete for database sustainable, what if database updates)
22. have read only vs edit mode (so saves from executing non-select statements by default with visual indicator)
23. ?add pagination to data tables (esp SQL can get big)
24. if error comes back, ability to have AI resolve (eg had SQL error)
25. if cycle through modes, make it blank, but if recycle to previous mode have what previously there
26. use pydantic-autocomplete (current drop down covers the entire cell)
27. terminal mode, show (like do with sql), information (like git branch, cwd, etc)
28. lets see if already code editor widget (because things like when typ "(" auto adds the other paranthesis)
29. try converting to UV backend (See why claude code had hatchling)

# agent file structure or suggester

1. redesign agent instructions so claude code and github copilot both keep working off one shared structure
    1. root AGENTS.md / .agents/ tree is copilot-authored today and isn't auto-loaded by claude code (it only reads CLAUDE.md)
    2. add a root CLAUDE.md that imports @AGENTS.md (or symlink) so claude code auto-loads the existing .agents/ tree at session start, without changing anything copilot/codex rely on
    3. add thin per-folder CLAUDE.md files (eg experimental/CLAUDE.md, pkgs/ds/CLAUDE.md) that import the matching .agents/instructions/*.md, since claude code auto-loads a directory's CLAUDE.md the moment it reads/edits a file there
    4. add experimental/ (and any other new top-level folders) to the Repo Structure + Scoped Guidance tables in .agents/agents.md
    5. confirm whether .agents/agents.md is actually regenerated by a copilot process before hand-editing it, so manual additions don't get silently clobbered not AGENTS.md")