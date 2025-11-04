# Custom System Prompts

**English** | [简体中文](../zh-CN/CUSTOM_SYSTEM_PROMPTS.md) | [繁體中文](../zh-TW/CUSTOM_SYSTEM_PROMPTS.md) | [日本語](../ja/CUSTOM_SYSTEM_PROMPTS.md) | [한국어](../ko/CUSTOM_SYSTEM_PROMPTS.md) | [हिन्दी](../hi/CUSTOM_SYSTEM_PROMPTS.md) | [Français](../fr/CUSTOM_SYSTEM_PROMPTS.md) | [Русский](../ru/CUSTOM_SYSTEM_PROMPTS.md) | [Español](../es/CUSTOM_SYSTEM_PROMPTS.md) | [Português](../pt/CUSTOM_SYSTEM_PROMPTS.md) | [Deutsch](../de/CUSTOM_SYSTEM_PROMPTS.md) | [Nederlands](../nl/CUSTOM_SYSTEM_PROMPTS.md)

This guide explains how to customize the system prompt that GAC uses to generate commit messages, allowing you to define your own commit message style and conventions.

## Table of Contents

- [Custom System Prompts](#custom-system-prompts)
  - [Table of Contents](#table-of-contents)
  - [What Are System Prompts?](#what-are-system-prompts)
  - [Why Use Custom System Prompts?](#why-use-custom-system-prompts)
  - [Quick Start](#quick-start)
  - [Writing Your Custom System Prompt](#writing-your-custom-system-prompt)
  - [Examples](#examples)
    - [Emoji-Based Commit Style](#emoji-based-commit-style)
    - [Team-Specific Conventions](#team-specific-conventions)
    - [Detailed Technical Style](#detailed-technical-style)
  - [Best Practices](#best-practices)
    - [Do:](#do)
    - [Don't:](#dont)
    - [Tips:](#tips)
  - [Troubleshooting](#troubleshooting)
    - [Messages still have "chore:" prefix](#messages-still-have-chore-prefix)
    - [AI ignoring my instructions](#ai-ignoring-my-instructions)
    - [Messages are too long/short](#messages-are-too-longshort)
    - [Custom prompt not being used](#custom-prompt-not-being-used)
    - [Want to switch back to default](#want-to-switch-back-to-default)
  - [Related Documentation](#related-documentation)
  - [Need Help?](#need-help)

## What Are System Prompts?

GAC uses two prompts when generating commit messages:

1. **System Prompt** (customizable): Instructions that define the role, style, and conventions for commit messages
2. **User Prompt** (automatic): The git diff data showing what changed

The system prompt tells the AI _how_ to write commit messages, while the user prompt provides the _what_ (the actual code changes).

## Why Use Custom System Prompts?

You might want a custom system prompt if:

- Your team uses a different commit message style than conventional commits
- You prefer emojis, prefixes, or other custom formats
- You want more or less detail in commit messages
- You have company-specific guidelines or templates
- You want to match your team's voice and tone
- You want commit messages in a different language (see Language Configuration below)

## Quick Start

1. **Create your custom system prompt file:**

   ```bash
   # Copy the example as a starting point
   cp custom_system_prompt.example.txt ~/.config/gac/my_system_prompt.txt

   # Or create your own from scratch
   vim ~/.config/gac/my_system_prompt.txt
   ```

2. **Add to your `.gac.env` file:**

   ```bash
   # In ~/.gac.env or project-level .gac.env
   GAC_SYSTEM_PROMPT_PATH=/path/to/your/custom_system_prompt.txt
   ```

3. **Test it:**

   ```bash
   gac --dry-run
   ```

That's it! GAC will now use your custom instructions instead of the default.

## Writing Your Custom System Prompt

Your custom system prompt can be plain text—no special format or XML tags required. Just write clear instructions for how the AI should generate commit messages.

**Key things to include:**

1. **Role definition** - What the AI should act as
2. **Format requirements** - Structure, length, style
3. **Examples** - Show what good commit messages look like
4. **Constraints** - What to avoid or requirements to meet

**Example structure:**

```text
You are a commit message writer for [your project/team].

When analyzing code changes, create a commit message that:

1. [First requirement]
2. [Second requirement]
3. [Third requirement]

Example format:
[Show an example commit message]

Your entire response will be used directly as the commit message.
```

## Examples

### Emoji-Based Commit Style

See [`custom_system_prompt.example.txt`](../../examples/custom_system_prompt.example.txt) for a complete emoji-based example.

**Quick snippet:**

```text
You are a commit message writer that uses emojis and a friendly tone.

Start each message with an emoji:
- 🎉 for new features
- 🐛 for bug fixes
- 📝 for documentation
- ♻️ for refactoring

Keep the first line under 72 characters and explain WHY the change matters.
```

### Team-Specific Conventions

```text
You are writing commit messages for an enterprise banking application.

Requirements:
1. Start with a JIRA ticket number in brackets (e.g., [BANK-1234])
2. Use formal, professional tone
3. Include security implications if relevant
4. Reference any compliance requirements (PCI-DSS, SOC2, etc.)
5. Keep messages concise but complete

Format:
[TICKET-123] Brief summary of change

Detailed explanation of what changed and why. Include:
- Business justification
- Technical approach
- Risk assessment (if applicable)

Example:
[BANK-1234] Implement rate limiting for login endpoints

Added Redis-based rate limiting to prevent brute force attacks.
Limits login attempts to 5 per IP per 15 minutes.
Complies with SOC2 security requirements for access control.
```

### Detailed Technical Style

```text
You are a technical commit message writer who creates comprehensive documentation.

For each commit, provide:

1. A clear, descriptive title (under 72 characters)
2. A blank line
3. WHAT: What was changed (2-3 sentences)
4. WHY: Why the change was necessary (2-3 sentences)
5. HOW: Technical approach or key implementation details
6. IMPACT: Files/components affected and potential side effects

Use technical precision. Reference specific functions, classes, and modules.
Use present tense and active voice.

Example:
Refactor authentication middleware to use dependency injection

WHAT: Replaced global auth state with injectable AuthService. Updated
all route handlers to accept AuthService through constructor injection.

WHY: Global state made testing difficult and created hidden dependencies.
Dependency injection improves testability and makes dependencies explicit.

HOW: Created AuthService interface, implemented JWTAuthService and
MockAuthService. Modified route handler constructors to require AuthService.
Updated dependency injection container configuration.

IMPACT: Affects all authenticated routes. No behavior changes for users.
Tests now run 3x faster with MockAuthService. Migration required for
routes/auth.ts, routes/api.ts, and routes/admin.ts.
```

## Best Practices

### Do

- ✅ **Be specific** - Clear instructions produce better results
- ✅ **Include examples** - Show the AI what good looks like
- ✅ **Test iteratively** - Try your prompt, refine based on results
- ✅ **Keep it focused** - Too many rules can confuse the AI
- ✅ **Use consistent terminology** - Stick to the same terms throughout
- ✅ **End with a reminder** - Reinforce that the response will be used as-is

### Don't

- ❌ **Use XML tags** - Plain text works best (unless you specifically want that structure)
- ❌ **Make it too long** - Aim for 200-500 words of instructions
- ❌ **Contradict yourself** - Be consistent in your requirements
- ❌ **Forget the ending** - Always remind: "Your entire response will be used directly as the commit message"

### Tips

- **Start with the example** - Copy `../../examples/custom_system_prompt.example.txt` and modify it
- **Test with `--dry-run`** - See the result without making a commit
- **Use `--show-prompt`** - See what's being sent to the AI
- **Iterate based on results** - If messages aren't quite right, adjust your instructions
- **Version control your prompt** - Keep your custom prompt in your team's repo
- **Project-specific prompts** - Use project-level `.gac.env` for project-specific styles

## Troubleshooting

### Messages still have "chore:" prefix

**Problem:** Your custom emoji messages are getting "chore:" added.

**Solution:** This shouldn't happen—GAC automatically disables conventional commit enforcement when using custom system prompts. If you see this, please [file an issue](https://github.com/cellwebb/gac/issues).

### AI ignoring my instructions

**Problem:** Generated messages don't follow your custom format.

**Solution:**

1. Make your instructions more explicit and specific
2. Add clear examples of the desired format
3. End with: "Your entire response will be used directly as the commit message"
4. Reduce the number of requirements—too many can confuse the AI
5. Try using a different model (some follow instructions better than others)

### Messages are too long/short

**Problem:** Generated messages don't match your length requirements.

**Solution:**

- Be explicit about length (e.g., "Keep messages under 50 characters")
- Show examples of the exact length you want
- Consider using `--one-liner` flag as well for short messages

### Custom prompt not being used

**Problem:** GAC still uses default commit format.

**Solution:**

1. Check that `GAC_SYSTEM_PROMPT_PATH` is set correctly:

   ```bash
   gac config get GAC_SYSTEM_PROMPT_PATH
   ```

2. Verify the file path exists and is readable:

   ```bash
   cat "$GAC_SYSTEM_PROMPT_PATH"
   ```

3. Check `.gac.env` files in this order:
   - Project level: `./.gac.env`
   - User level: `~/.gac.env`
4. Try an absolute path instead of relative path

### Language Configuration

**Note:** You don't need a custom system prompt to change the commit message language!

If you only want to change the language of your commit messages (while keeping the standard conventional commit format), use the interactive language selector:

```bash
gac language
```

This will present an interactive menu with 25+ languages in their native scripts (Español, Français, 日本語, etc.). Select your preferred language, and it will automatically set `GAC_LANGUAGE` in your `~/.gac.env` file.

Alternatively, you can manually set the language:

```bash
# In ~/.gac.env or project-level .gac.env
GAC_LANGUAGE=Spanish
```

By default, conventional commit prefixes (feat:, fix:, etc.) remain in English for compatibility with changelog tools and CI/CD pipelines, while all other text is in your specified language.

**Want to translate prefixes too?** Set `GAC_TRANSLATE_PREFIXES=true` in your `.gac.env` for full localization:

```bash
GAC_LANGUAGE=Spanish
GAC_TRANSLATE_PREFIXES=true
```

This will translate everything, including prefixes (e.g., `corrección:` instead of `fix:`).

This is simpler than creating a custom system prompt if language is your only customization need.

### Want to switch back to default

**Problem:** Want to temporarily use default prompts.

**Solution:**

```bash
# Option 1: Unset the environment variable
gac config unset GAC_SYSTEM_PROMPT_PATH

# Option 2: Comment it out in .gac.env
# GAC_SYSTEM_PROMPT_PATH=/path/to/custom_prompt.txt

# Option 3: Use a different .gac.env for specific projects
```

---

## Related Documentation

- [USAGE.md](USAGE.md) - Command-line flags and options
- [README.md](../../README.md) - Installation and basic setup
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - General troubleshooting

## Need Help?

- Report issues: [GitHub Issues](https://github.com/cellwebb/gac/issues)
- Share your custom prompts: Contributions welcome!
