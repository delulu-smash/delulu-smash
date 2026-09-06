# PC Tools
1. using "glow" to write documentation in markdwon but omarchy short cut to render (as way to easily view local docs fast, eg common links, etc)
2. install screen recorder to gif
3. create dsu command to publish changes easily
4. have AI
    1. help create convert to gif utility and have screenrecorder be gif instead (or option to), also may want to use for CLI tool, website, etc

# Smash Package and Tooling
1. use AI to convert smash utlimate data site code to python (with tests, documentation, etc, do this one on specific branch so perhaps can easily trash)
2. have a labbing tool, where has
    1. easy information eg fastest mash options MU has
    2. auto links to staging folder, so can easily view vid recorded (and go frame by frame), option to make gif (store in cloud flare)
    3. any other things that would make fast to document

# AI
1. learning more on skills (eg looks like github copilot downloaded skills on own like files below
    1. /home/kdaftari/.agents/skills/omarchy/SKILL.md
    2. /opt/visual-studio-code/resources/app/extensions/copilot/assets/prompts/skills/create-agent/SKILL.md
    3. user memory: /home/kdaftari/.config/Code/User/globalStorage/github.copilot-chat/memory-tool/memories/script-preferences.md
2. recreate pkgs via AI so can get the styling and such down so can move faster with AI later
3. skill files for python (so has proper linting and formatting that uv uses, and start to document my style, perhaps make representative scirpt and have AI tell what think style is and edit with it via conversation and explanation)
4. create MCP server for my library? https://code.visualstudio.com/docs/agent-customization/mcp-servers?referrer=in-product
5. using litellm (https://docs.litellm.ai/docs/proxy/ui) to test which ai is better (claude may be better as can cache prompts which useful if loading lot of skill files). Ideally i could have it read from existing skill and prompt files so the repo AI and app AI stay aligned
    1. prompt caching https://docs.litellm.ai/docs/completion/prompt_caching
6. using pydnatic-ai to create a smash ai agent, which will have cli prompt tool and reflex ui forhttps://youtu.be/PY7xIxybYNc?is=NV3bopZXPFyjVJM6
7. have the ai able to be run in tui like toad: https://youtu.be/fSE44AuiC8k?is=uBZqbdg56AZKeNxV (textual allows to host on browser as well)
8. adding cron job to keep smashdb data up to date (run cli command, commit new parquet files)
9. Skill files that help with
    1. querying smashdb (need general SQL capability, smash database schema knowledge)
    2. ability to have smash knoweledge base that reads appropriate docs with additional
    specific AI items (eg what synonms are there, etc - may need to separate from base vs deep)

# TUI
1. create own AI Tui
2. has jupyter like capabilities (ability to play with data an agent creates, store the context variables)
3. ability to AI edit code cells
4. have vibe coded so can have 3 repos (PI, claude Code, toad), and learn from each
and see differences, so can vibe code and edit project as those get updates
5. separate module for more true best practices (Eg how claude remembers sessions, auto runs, was able test and examine and SVG to see visual issue of textual, etc). Want to get TUI as smart as claude code as possible
6. serve TUI as web tool so can have people as AI query tool
  1. have this added to AI project understanding, so features like copy to clipboard of table work
7. have SQL mode
8. review code and have rewrite so can be own package, and see code quality, and have skill that develops embedding my personal coding principals (research other skill files)
9. have way to modes for each resource (eg api, database, etc), ability to create own
10. publish this as open source pypi package so i can use for work
6. try out https://github.com/features/ai/github-app?utm_source=copilot-cli-nudge (and see how compares to just vscode or github cli)
7. look at omarchy video on how create own branding, and have it be the mac icon have as favcon for my delulu smash site
