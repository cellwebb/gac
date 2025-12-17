# Changelog

## [2025-12-17] - v0.18.1

### What's New

- New setting to automatically add a scope to your commit messages, so you don’t have to type it each time.
- Reroll command now accepts your own hint, letting you guide the regenerated commit message.

### Improvements

- The AI now separates system and user prompts, giving more focused and accurate suggestions.
- Anthropic token counting has been refined, making the tool faster and more reliable.
- Commit type detection gives higher priority to code changes over documentation, improving labeling.

### Bug Fixes

- Fixed a crash that could happen when using the -p flag to push changes.
- Corrected the way pure documentation updates are labeled, preventing wrong ‘docs:’ tags.
- Pre‑commit hook failures now show the full error output, helping you understand what went wrong.

---

## [2025-12-17] - v0.19.0

### Improvements

- The scope option is now a simple on/off switch that automatically determines the right scope, so you don’t have to type it yourself.
- Help messages and prompts have been updated to explain the new automatic scope detection, making it easier to understand what to do.
- The app now runs more smoothly and reliably thanks to updated formatting rules and behind‑the‑scenes improvements.

---

## [2025-12-17] - v0.19.1

### Improvements

- AI assistance works more reliably and gives better results
- Data entry checks are more accurate, reducing mistakes
- Command‑line interface looks cleaner and is easier to read

---

## [2025-12-17] - v1.0.0

### Improvements

- AI features are now more reliable thanks to direct connections to AI services
- AI responses load faster and automatically retry if a request temporarily fails
- Error messages are clearer when an AI service encounters a problem

---

## [2025-12-17] - v1.0.1

### Improvements

- Improved token counting reliability with online service, fallback estimation when no key, and clearer error messages

---

## [2025-12-17] - v1.1.0

### What's New

- You can now generate commit messages using the OpenRouter AI service

### Improvements

- Error messages from the AI helper are clearer, helping you understand what went wrong
- The app now estimates AI usage more accurately, leading to smoother performance

---

## [2025-12-17] - v1.2.0

### Improvements

- Generating commit message suggestions is now more reliable and recovers automatically if a temporary problem occurs.
- The app handles both single phrases and lists when creating suggestions, so you get results in either format.
- Behind the scenes the process has been streamlined, making suggestion generation faster and smoother.

---

## [2025-12-17] - v1.2.1

### Improvements

- AI responses are now more reliable and less likely to fail
- Errors during AI generation are handled more gracefully with clearer messages
- Token counting is more robust, preventing issues with long prompts

---

## [2025-12-17] - v1.2.2

### Improvements

- Simplified OpenRouter setup by removing unused site URL and name options
- Documentation updated to show the new, streamlined configuration

---

## [2025-12-17] - v1.2.3

### Bug Fixes

- Fixed an issue where the token limit for AI responses was set incorrectly, preventing errors

---

## [2025-12-17] - v1.2.4

### Improvements

- Added thorough checks for AI features to improve reliability

---

## [2025-12-17] - v1.2.5

### What's New

- You can now generate commit messages using Z.AI, a new AI assistant

### Improvements

- Better handling when selecting AI assistants, so error messages are clearer
- Documentation now includes Z.AI among the available AI assistants

---

## [2025-12-17] - v1.2.6

### Improvements

- Enhanced testing framework for AI features, helping ensure smoother and more reliable performance

---

## [2025-12-17] - v1.3.0

### What's New

- You can now enable a special coding mode for Z.AI to get code‑focused help

### Improvements

- Secret scanning now finds more kinds of passwords and keys while showing fewer false alarms
- Warning messages about secret files are clearer and the prompts are easier to understand
- When the AI service is busy or limits requests, the app now waits gracefully instead of stopping

### Bug Fixes

- Fixed confusing wording when you abort a commit after a security warning

---

## [2025-12-17] - v1.3.1

### What's New

- Added new Zai AI provider for smarter assistance

---

## [2025-12-17] - v1.4.0

### What's New

- New Z.AI Coding option lets you generate code directly within the app

### Improvements

- Setup is easier now – you no longer have to configure extra settings
- All Z.AI features share the same key, making configuration simpler
- Choosing Z.AI services during setup is clearer and more straightforward

---

## [2025-12-17] - v1.4.1

### What's New

- New AI coding assistant available for generating code suggestions

### Improvements

- AI assistant works more reliably
- Simpler setup by removing an unnecessary option

### Bug Fixes

- Fixed occasional errors when using AI generation features

---

## [2025-12-17] - v1.4.2

### Improvements

- Prompt templates are now handled with a simpler method, so creating prompts works more smoothly
- Error messages related to prompts are clearer and no longer show confusing internal tags
- Behind‑the‑scenes simplifications make prompt processing a bit faster

---

## [2025-12-17] - v1.5.0

### What's New

- You can now connect the app to Gemini and LM Studio AI services, and also use Ollama by entering your access code

### Improvements

- The app now handles empty replies from AI services more gracefully, preventing hangs
- Help pages now include clear examples for setting up the new AI services

### Bug Fixes

- Fixed a setup problem with Gemini that could cause errors during configuration

---

## [2025-12-17] - v1.5.1

### Improvements

- Updated message format to match the latest Gemini service, making chats feel more natural
- Added ability to include system instructions, giving you more control over responses
- Clearer error messages help you understand what went wrong faster

### Bug Fixes

- Fixed crashes when the Gemini service returns incomplete data
- Prevented errors caused by missing content parts or candidates in responses

---

## [2025-12-17] - v1.5.2

### What's New

- New StreamLake AI provider is now available for generating content

### Improvements

- You can now add optional access keys and custom server URLs for Ollama and LM Studio, making setup easier
- The command‑line tool better guides you through the initial configuration steps

### Bug Fixes

- Error message now clearly tells you to run ‘gac init’ when the configuration hasn’t been set up

---

## [2025-12-17] - v1.6.0

### What's New

- Added a new synthetic AI option, letting you use the GLM‑4.6 model out of the box

### Improvements

- Clearer messages if sign‑in fails or a request times out
- Notifies you when requests are limited and advises when to try again
- Updated to work with the latest system version for improved stability

---

## [2025-12-17] - v1.7.0

### Improvements

- Updated guides with clearer steps for setting up the app and running it on the latest Python versions
- Added a new option to include your Synthetic service key in the configuration example, making it easier to get started

### Bug Fixes

- Fixed a problem where the Synthetic service didn’t work if the model name was entered without the “hf:” prefix

---

## [2025-12-17] - v1.8.0

### What's New

- Added support for Chutes.ai, letting you use its AI services directly from the app

### Bug Fixes

- Fixed a problem with Anthropic AI selection so it works with the newest version
- Corrected the LM Studio name in the list, ensuring it appears correctly

---

## [2025-12-17] - v1.9.0

### What's New

- Added a new detailed mode that creates longer, structured commit messages with sections like motivation and impact

### Improvements

- You can now enable the detailed mode permanently through a setting, so you don’t have to turn it on each time

---

## [2025-12-17] - v1.9.1

### What's New

- New –verbose option lets you create detailed, structured commit messages

### Bug Fixes

- Added support for the Chutes AI provider
- Fixed the name of the LM‑Studio provider so it works correctly

---

## [2025-12-17] - v1.9.2

### Improvements

- Service names now appear correctly, so you’ll see “Chutes” instead of a confusing label

### Bug Fixes

- Fixed an issue that prevented the LM Studio connection from working properly
- Ensured service names are displayed consistently across the app

---

## [2025-12-17] - v1.9.3

### Improvements

- App is now more stable and reliable thanks to additional testing and quality checks

---

## [2025-12-17] - v1.9.4

### Improvements

- Now provides longer, more detailed responses from advanced AI

---

## [2025-12-17] - v1.9.5

### Improvements

- Removed unused features, making the app lighter and faster
- Improved help pages with clearer steps, better layout, and fun emojis for easier start-up
- Switched wording from “AI” to “LLM” throughout the app and guides for more accurate description

### Bug Fixes

- Fixed a problem where token usage numbers were wrong after changing prompts, now the count is accurate

---

## [2025-12-17] - v1.10.0

### What's New

- Added support for Fireworks AI, so you can generate content using this new AI service

### Improvements

- Getting started is simpler: the quick‑start guide now shows the fastest way to run the tool without installing anything first
- The help page now includes friendly emoji icons, making it easier to find the sections you need
- The AI now keeps track of earlier messages, giving more relevant suggestions when you refine your requests

---

## [2025-12-17] - v1.10.1

### Improvements

- Automated code checks now run faster, speeding up contribution processes

---

## [2025-12-17] - v1.10.2



---

## [2025-12-17] - v1.10.3

### What's New

- New Together AI integration lets you generate content with Together AI models

### Improvements

- Enhanced command explanations and examples make it easier to understand how to stage changes, use verbose output, and handle trivial edits
- Refined project description highlights benefits and outcomes, helping you see what the tool provides

---

## [2025-12-17] - v1.11.0

### What's New

- New Minimax AI helper can suggest commit messages automatically

### Improvements

- AI suggestions are now more reliable, handling login issues and slow responses better

---

## [2025-12-17] - v1.11.1

### What's New

- You can now choose Together AI as a new AI option, using a powerful built‑in model

---

## [2025-12-17] - v1.12.0

### What's New

- New DeepSeek option lets you generate content with a different AI model

---

## [2025-12-17] - v1.12.1

### Improvements

- Made the app handle special system instructions more smoothly for better AI interactions
- Enhanced the way the app reads AI responses, so answers are more reliable
- Added extra testing to keep the app stable over time

### Bug Fixes

- Fixed a problem where using special system prompts with Gemini caused errors, preventing crashes
- Fixed an issue where Gemini sometimes returned empty parts, leading to incomplete answers

---

## [2025-12-17] - v1.13.0

### What's New

- Connect to custom Anthropic or OpenAI endpoints, including Azure and self‑hosted services

### Improvements

- Setup guide now walks you through entering the custom endpoint URL and API key
- Help screen images now show dark‑mode view and load faster

---

## [2025-12-17] - v1.13.1

### Improvements

- AI responses no longer include stray <think> tags, making the output cleaner
- Multi‑line reasoning tags are removed correctly, even if they appear in different cases
- Provider list now uses correct plural wording for custom endpoints, improving clarity

---

## [2025-12-17] - v1.14.0

### What's New

- You can now load your own custom system prompts to guide the tool’s behavior

### Improvements

- Generated text now includes line breaks, making it easier to read

---

## [2025-12-17] - v1.15.0

### What's New

- Choose the language for your commit messages from over 25 options
- Option to translate standard labels (like “feat” or “fix”) into the chosen language
- Add a –-language flag to quickly set the language for a single commit

### Improvements

- Enter language codes (es, zh‑CN, ja, etc.) as a shortcut for selecting a language
- If language selection is cancelled or invalid, the tool now safely falls back to English

---

## [2025-12-17] - v2.0.0

### Improvements

- You can now type feedback directly without any special prefix, and an empty input will bring the prompt back for you.
- Prompt wording has been updated to clearly show you can write custom messages, making the interaction easier to understand.
- Commit message rules are more flexible: no character limit for one‑line messages and clearer guidance for multi‑line messages.

---

## [2025-12-17] - v2.1.0

### What's New

- Added support for Mistral AI to generate commit messages

### Improvements

- Updated default Cerebras model to the newer zai-glm-4.6 for better results
- Shortened language command with a new 'lang' alias for quicker use
- Revised getting‑started guide with clearer steps and new screenshots

---

## [2025-12-17] - v2.2.0

### What's New

- Edit commit messages directly while working, using a full-screen editor with familiar vi/emacs shortcuts

### Improvements

- Process larger codebases and more complex changes thanks to doubled token limits
- Enhanced message editor UI with a hint bar, scrollbar and new Ctrl+S shortcut for easier navigation of long messages

---

## [2025-12-17] - v2.3.0



---

## [2025-12-17] - v2.4.0



---

## [2025-12-17] - v2.4.1

### Improvements

- Improved handling of unexpected errors, making the app more reliable during background operations

---

## [2025-12-17] - v2.5.0

### What's New

- You can now adjust the timeout for automated checks during commits, preventing long runs from stopping unexpectedly

### Improvements

- Documentation is now grouped by language, making it easier to find help in your preferred language
- Screenshots and diagrams in translated guides now appear correctly

---

## [2025-12-17] - v2.5.1

### Improvements

- Default timeout now set to 120 seconds when not specified, so tasks run without unexpected delays

### Bug Fixes

- Fixed a crash that occurred when the timeout setting was missing

---

## [2025-12-17] - v2.5.2



---

## [2025-12-17] - v2.6.0

### What's New

- You can now sign in using Claude Code, Anthropic’s AI assistant, for a smoother and more secure login experience

### Improvements

- Claude Code sign‑in now automatically refreshes when needed, so you won’t be logged out unexpectedly
- Help pages now include step‑by‑step Claude Code guides in 16 languages, with direct links from the main usage and troubleshooting sections
- Additional behind‑the‑scenes checks have been added, making the app more stable during sign‑in and everyday use

### Bug Fixes

- Fixed an issue where a required system message had to be exact, which previously prevented successful Claude Code sign‑in

---

## [2025-12-17] - v2.6.1

### What's New

- App now automatically refreshes your login when it expires, so you stay signed in without extra steps

### Improvements

- Simplified setup guide – the extra ‘model’ command has been removed, making the start process clearer
- More reliable sign‑in experience with clearer messages and smoother handling of unexpected issues

### Bug Fixes

- Fixed a crash that could happen when saved login information was missing
- Fixed occasional sign‑in errors that occurred during network problems

---

## [2025-12-17] - v2.7.0

### What's New

- New dedicated sign‑in command makes logging in quicker and easier

### Improvements

- Re‑login no longer requires navigating extra menus
- Clearer messages guide you through login and the browser opens automatically

---

## [2025-12-17] - v2.7.1

### Improvements

- Easier fix for expired sign‑in tokens: just run the quick command to re‑authenticate.
- Interactive setup questions now let you move with arrow keys and shortcut keys, making selections faster.
- Login help guide is clearer with separate sections and step‑by‑step instructions in all languages.

---

## [2025-12-17] - v2.7.2

### Improvements

- App counts words for local AI models faster by avoiding unnecessary internet checks
- Token counting now works reliably even if model details are missing

### Bug Fixes

- Fixed occasional crashes when estimating token usage for local providers

---

## [2025-12-17] - v2.7.3

### What's New

- You can now keep the app completely offline by disabling token‑counting downloads

### Improvements

- Provider lists in the help guide are easier to read
- Help guide now explains the new offline option in many languages

---

## [2025-12-17] - v2.7.4

### Improvements

- Improved help pages with a clearer list of supported services, added Thai language support, and new info about the optional GAC_NO_TIKTOKEN setting
- Provider names in the selection menu now match their official sites (e.g., MiniMax.io, Synthetic.new) for easier identification

---

## [2025-12-17] - v2.7.5

### Improvements

- Enhanced handling of right‑to‑left language warnings, so you get accurate alerts
- Improved reliability of prompts during configuration, preventing accidental interruptions

### Bug Fixes

- Fixed a problem where cancelling a prompt could cause the app to freeze

---

## [2025-12-17] - v3.0.0

### What's New

- You can now keep settings specific to each project using a .gac.env file in the project folder

### Improvements

- Configuration now only looks for .gac.env files, making setup simpler and more predictable
- When viewing configuration, user‑level and project‑level settings are clearly labeled, showing which values take priority

---

## [2025-12-17] - v3.1.0

### Improvements

- More reliable connections to external services, reducing unexpected errors
- Adding and managing supported services is now smoother, making setup easier
- Consistency checks run behind the scenes, so features work together more predictably

---

## [2025-12-17] - v3.2.0

### What's New

- Added support for Replicate AI, so you can generate results using Replicate's models

### Improvements

- Switched the default AI model to the newer gpt-5-mini, offering faster and more accurate responses

---

## [2025-12-17] - v3.3.0

### What's New

- You can now include renamed files in grouped commits, keeping their history intact
- A new --message-only option lets you see just the generated commit message without making any changes

### Improvements

- Help pages now show the --message-only option in 16 languages with clear examples

---

## [2025-12-17] - v3.4.0

### What's New

- You can now choose from three new AI services: Kimi Coding, Moonshot AI, and Azure OpenAI.

### Improvements

- Help pages now list all supported AI services and give clearer guidance.
- Adding a new AI service is simpler with a shorter, easier checklist.
- Entering your access keys is easier—names are adjusted automatically for compatibility.

---

## [2025-12-17] - v3.4.1



---

## [2025-12-17] - v3.4.2

### Improvements

- Updated default AI models to the latest versions, so you get the newest capabilities automatically

---

## [2025-12-17] - v3.4.3

### Bug Fixes

- Fixed a problem that prevented the Kimi coding feature from being recognized

---

## [2025-12-17] - v3.5.0

### What's New

- Choose from over 26 AI services, including Azure OpenAI, directly in the setup
- New sign‑in option for Claude Code that guides you through a secure login
- Support for local AI tools like Ollama and LM Studio, with optional login

### Improvements

- Setup now shows clearer success messages so you know everything is ready
- Language selection during setup is smoother and lets you cancel easily
- Documentation now lists all supported services in an easier‑to‑read layout

### Bug Fixes

- Fixed incorrect names for Kimi and Zai services so they work correctly
- Corrected the environment variable used for Zai login
- Fixed a command‑line testing issue that could cause unexpected behavior

---

## [2025-12-17] - v3.6.0

### What's New

- Interactive mode lets you answer a few questions when committing, producing more accurate and detailed commit messages.

### Improvements

- Loading messages during the question step are clearer and look the same across the app.
- The tool no longer includes an unused component, making start‑up a bit faster.
- Warning messages about large token counts are now clearer, helping you understand when a commit is stopped.

---

## [2025-12-17] - v3.6.1

### What's New

- The tool now asks the right number of questions based on how big your change is, giving you fewer prompts for tiny edits and more for larger ones, so the experience feels smoother

---

## [2025-12-17] - v3.6.2

### Bug Fixes

- Fixed inability to move cursor left/right during interactive input, allowing easier editing

---

## [2025-12-17] - v3.6.3

### Improvements

- Improved reliability of error messages and handling across the app
- Enhanced setup prompts to guide you through configuration and handle cancellations smoothly
- Strengthened support for AI provider setup, ensuring smoother configuration and re‑authentication

---

## [2025-12-17] - v3.6.4

### Bug Fixes

- Commit messages are now cleaned up, removing any extra spaces before they are saved

---

## [2025-12-17] - v3.7.0



---

## [2025-12-17] - v3.7.1

### What's New

- Automatic login for Qwen AI, so you stay signed in without extra steps
- The app now re‑signs you in automatically if the Qwen session expires

### Improvements

- Clearer messages when the Qwen sign‑in process runs
- Better handling of sign‑in errors, giving helpful prompts instead of crashes

---

## [2025-12-17] - v3.8.0

### What's New

- Added a --no-verify-ssl option so you can skip SSL checks when using corporate proxy servers

### Improvements

- Documentation now includes clear examples and do‑don’t guidance for AI agent commands

---

## [2025-12-17] - v3.8.1



---

## [2025-12-17] - v3.8.2

### Improvements

- Added extra security for Qwen communications, keeping your data safe

---

## [2025-12-17] - v3.9.0

### Improvements

- All AI services now share a common foundation, so they work more consistently and reliably
- Claude Code now uses an OAuth token store, letting you log in once and stay signed in
- Providers load only when you use them, making the app start faster and use less memory

### Bug Fixes

- Azure OpenAI provider now builds correct URLs even when the model name is missing
- Connection‑error messages from LM Studio are now clearer and no longer cause freezes

---

## [2025-12-17] - v3.9.1

### Improvements

- Settings list is now shown alphabetically for easier browsing

### Bug Fixes

- Sensitive information like keys and passwords is now hidden when viewing settings

---

## [2025-12-17] - v3.9.2

### Bug Fixes

- Fixed error messages for incomplete model specifications like "openai:" or ":gpt-4", now clearly telling you both provider and model name are required

---

## [2025-12-17] - v3.9.3

### Improvements

- More specific error handling means the app now shows clearer messages and avoids unexpected shutdowns.
- Configuration files are now validated more accurately, so settings are loaded reliably.
- App updated to version 3.9.3 with behind-the-scenes stability enhancements.

---

## [2025-12-17] - v3.10.0

### Improvements

- Error messages now hide any secret keys or tokens and are shortened, so your private information stays safe
- All errors are now handled in the same way, giving you clearer and more reliable messages when something goes wrong
- Setting up external services is now simpler, with automatic setup that works smoothly without extra steps

---

## [2025-12-17] - v3.10.1

### What's New

- The tool now scans your changes for passwords or keys and warns you before committing.
- An interactive mode asks you simple questions to help create clearer commit messages.
- You can group several file changes together and get one AI‑suggested commit for the whole set.

### Improvements

- Repository checks are more reliable, catching problems early and giving clearer messages.
- Prompt displays are faster and easier to read while the tool runs.
- File renames and staging are handled more smoothly, reducing unexpected errors.

---

## [2025-12-17] - v3.10.2

### Improvements

- Commit confirmation now always shows the message panel and lets you cancel cleanly with a "no" response

---

## [2025-12-17] - v3.10.3

### Improvements

- Simplified error handling for more reliable operation
- Full type checking added, reducing hidden bugs and improving stability
- Unused code cleaned up, helping the app run faster and smoother

### Bug Fixes

- Fixed crashes that could happen with certain error messages
- Removed old testing code that sometimes caused the app to freeze

---

## [2025-12-17] - v3.10.4



---

## [2025-12-17] - v3.10.6

### Improvements

- Added smarter handling of model identifiers, giving clear feedback if the format is wrong
- Authentication now automatically refreshes expired tokens and retries, reducing sign‑in interruptions
- Internal reorganization improves stability and makes future updates smoother

---

## [2025-12-17] - v3.10.7

### Improvements

- Simplified workflow handling for smoother performance

---

## [2025-12-17] - v3.10.8

### Improvements

- The app now exits more smoothly, avoiding abrupt shutdowns
- Clearer messages are shown when automatic code checks fail

---

## [2025-12-17] - v3.10.9

### Improvements

- Generated messages are now cleaner, without stray tags or formatting glitches
- Responses are faster and more reliable thanks to optimized template handling
- Overall stability has been boosted by internal clean‑up

---

## [2025-12-17] - v3.10.10

### Improvements

- Improved reliability when committing changes; the app now restores your original state if a commit or push fails.

### Bug Fixes

- Fixed a problem where interrupted commits could leave the staging area inconsistent, preventing data loss.

---

## [2025-12-17] - v3.10.11

### Improvements

- Added more thorough checks for dry‑run mode, so simulated commits behave more reliably
- Strengthened handling of questions and answers, improving accuracy when parsing lists or incomplete responses
- Updated documentation on test coverage goals, showing progress toward higher reliability

---

## [2025-12-17] - v3.10.12

### Improvements

- The app now handles missing or extra files more gracefully, preventing unexpected stops
- Error messages now include clearer details, making it easier to understand what went wrong
- Added extra safety checks to catch unusual situations, reducing the chance of crashes

---

## [2025-12-17] - v3.10.13

### Improvements

- Dynamic service URLs are now built automatically for Anthropic‑compatible providers, making setup easier
- Improved handling of large file token warnings, letting you accept, decline, or retry when needed
- More reliable right‑to‑left language detection and text centering for better display

---

## [2025-12-17] - v3.10.14

### Improvements

- The app now handles unexpected errors during content generation more gracefully, showing clearer messages and retrying automatically
- Signing in and connecting to AI services works more reliably, reducing setup problems
- Cancelling actions or using quiet mode no longer cause the app to freeze, giving a smoother experience

---

## [2025-12-17] - v3.10.15

### Bug Fixes

- Fixed a problem that could prevent the Mistral model from loading by updating its identifier to the latest naming

---

## [2025-12-17] - v3.10.16



---

## [2025-12-17] - v3.10.17

### Bug Fixes

- Fixed missing fallback message when the browser fails to open

---

## [2025-12-17] - v3.11.0

### What's New

- New commands let you view, edit, import from a file, or clear a custom system prompt directly from the tool

### Improvements

- The version command now shows a clear list of what changed in each release, so you can see updates at a glance
- Prompt commands now always display the most current default text when no custom prompt is set
- Simplified the prompt commands by removing an unnecessary option, making the interface cleaner

---

## [2025-12-17] - v1.1.0

### What's New

- OpenRouter is now supported for AI-generated commit messages

### Improvements

- AI features now show clearer messages when something goes wrong
- Word counting is more accurate, helping keep AI suggestions within limits

---

## [2025-12-17] - v0.18.1



---

## [2025-12-17] - v1.0.1

### Improvements

- AI word count now uses an online service for more accurate results
- Counting still works even without a key by using a backup method
- Clearer messages appear if counting encounters a problem

---

## [2025-12-17] - v0.18.1



---

## [2025-12-17] - v0.18.1



---

## [2025-12-17] - v0.19.0

### Improvements

- The scope option now works as a simple on/off switch that automatically figures out the right scope for you.
- Help messages and usage examples have been clarified, making it easier to understand how the scope setting works.
- Version updated to 0.18.1 with behind‑the‑scenes stability and consistency upgrades.

---

## [2025-12-17] - v0.19.1

### Improvements

- Updated AI components for more reliable performance
- Enhanced data checks for fewer errors
- Refreshed command‑line appearance and smoother interaction

---

## [2025-12-17] - v1.0.0

### Improvements

- AI-powered features now connect directly to the online service, so they work more reliably
- If an AI request fails, the app automatically tries again, reducing interruptions
- Error messages from AI features are clearer, helping you understand what went wrong