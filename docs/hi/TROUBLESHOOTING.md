# Troubleshooting gac

[English](../en/TROUBLESHOOTING.md) | [简体中文](../zh-CN/TROUBLESHOOTING.md) | [繁體中文](../zh-TW/TROUBLESHOOTING.md) | [日本語](../ja/TROUBLESHOOTING.md) | [한국어](../ko/TROUBLESHOOTING.md) | **हिन्दी** | [Français](../fr/TROUBLESHOOTING.md) | [Русский](../ru/TROUBLESHOOTING.md) | [Español](../es/TROUBLESHOOTING.md) | [Português](../pt/TROUBLESHOOTING.md) | [Deutsch](../de/TROUBLESHOOTING.md) | [Nederlands](../nl/TROUBLESHOOTING.md)

यह गाइड gac को इंस्टॉल करने, कॉन्फ़िगर करने और चलाने के लिए सामान्य समस्याओं और समाधानों को कवर करता है।

## Table of Contents

- [Troubleshooting gac](#troubleshooting-gac)
  - [Table of Contents](#table-of-contents)
  - [1. Installation Problems](#1-installation-problems)
  - [2. Configuration Issues](#2-configuration-issues)
  - [3. Provider/API Errors](#3-providerapi-errors)
  - [4. Commit Grouping Issues](#4-commit-grouping-issues)
  - [5. Security and Secret Detection](#5-security-and-secret-detection)
  - [6. Pre-commit and Lefthook Hook Issues](#6-pre-commit-and-lefthook-hook-issues)
  - [7. Common Workflow Issues](#7-common-workflow-issues)
  - [8. General Debugging](#8-general-debugging)
  - [Still Stuck?](#still-stuck)
  - [Where to Get Further Help](#where-to-get-further-help)

## 1. Installation Problems

**Problem:** `gac` command not found after install

- सुनिश्चित करें कि आपने `uv tool install gac` या `uvx gac` के साथ इंस्टॉल किया है
- यदि आपने `uv tool install` का उपयोग किया है, तो `uv tool list` के साथ इंस्टॉलेशन सत्यापित करें
- सुनिश्चित करें कि `uv` इंस्टॉल है और आपके `$PATH` में है
- इंस्टॉलेशन के बाद अपना टर्मिनल रीस्टार्ट करें

**Problem:** Permission denied or cannot write files

- डायरेक्टरी अनुमतियाँ जांचें
- उचित विशेषाधिकारों के साथ चलाने का प्रयास करें या डायरेक्टरी स्वामित्व बदलें

## 2. Configuration Issues

**Problem:** gac can't find your API key or model

- यदि आप नए हैं, तो अपने provider, model, और API keys को इंटरैक्टिव रूप से सेट करने के लिए `gac init` चलाएं
- सुनिश्चित करें कि आपका `.gac.env` या environment variables सही तरीके से सेट हैं
- कौन सी config फाइलें लोड हो रही हैं और configuration issues को डीबग करने के लिए `gac --log-level=debug` चलाएं
- वेरिएबल नामों में टाइपो के लिए जांचें (जैसे `GAC_GROQ_API_KEY`)

**Problem:** User-level `$HOME/.gac.env` changes are not picked up

- सुनिश्चित करें कि आप अपने OS के लिए सही फाइल संपादित कर रहे हैं:
  - macOS/Linux पर: `$HOME/.gac.env` (आमतौर पर `/Users/<your-username>/.gac.env` या `/home/<your-username>/.gac.env`)
  - Windows पर: `$HOME/.gac.env` (आमतौर पर `C:\Users\<your-username>\.gac.env` या `%USERPROFILE%` का उपयोग करें)
- User-level config लोड हो रहा है यह पुष्टि करने के लिए `gac --log-level=debug` चलाएं
- Environment variables को रीलोड करने के लिए अपना टर्मिनल रीस्टार्ट करें या अपना shell फिर से चलाएं
- यदि फिर भी काम नहीं कर रहा है, तो टाइपो और फाइल अनुमतियों के लिए जांचें

**Problem:** Project-level `.gac.env` changes are not picked up

- सुनिश्चित करें कि आपका प्रोजेक्ट रूट डायरेक्टरी में (आपके `.git` फोल्डर के बगल में) एक `.gac.env` फाइल है
- Project-level config लोड हो रहा है यह पुष्टि करने के लिए `gac --log-level=debug` चलाएं
- यदि आप `.gac.env` संपादित करते हैं, तो environment variables को रीलोड करने के लिए अपना टर्मिनल रीस्टार्ट करें या अपना shell फिर से चलाएं
- यदि फिर भी काम नहीं कर रहा है, तो टाइपो और फाइल अनुमतियों के लिए जांचें

**Problem:** Cannot set or change language for commit messages

- 25+ समर्थित भाषाओं से इंटरैक्टिव रूप से चुनने के लिए `gac language` (या `gac lang`) चलाएं
- एकल कमिट के लिए भाषा को ओवरराइड करने के लिए `-l <language>` फ्लैग का उपयोग करें (जैसे `gac -l zh-CN`, `gac -l Spanish`)
- वर्तमान भाषा सेटिंग देखने के लिए `gac config show` के साथ अपनी config जांचें
- भाषा सेटिंग आपकी `.gac.env` फाइल में `GAC_LANGUAGE` में संग्रहीत है

## 3. Provider/API Errors

**Problem:** Authentication or API errors

- सुनिश्चित करें कि आपने अपने चुने हुए मॉडल के लिए सही API keys सेट किए हैं (जैसे `ANTHROPIC_API_KEY`, `GROQ_API_KEY`)
- अपनी API key और provider खाता स्थिति की दोबारा जांच करें
- Ollama और LM Studio के लिए, पुष्टि करें कि API URL आपके स्थानीय instance से मेल खाता है। API keys केवल तभी आवश्यक हैं यदि आपने प्रमाणीकरण सक्षम किया है।

**Problem:** Model not available or unsupported

- Streamlake inference endpoint IDs का उपयोग करता है मॉडल नामों के बजाय। सुनिश्चित करें कि आप उनके console से endpoint ID supply करते हैं।
- सत्यापित करें कि मॉडल नाम सही है और आपके provider द्वारा समर्थित है
- उपलब्ध मॉडल के लिए provider documentation जांचें

## 4. Commit Grouping Issues

**Problem:** `--group` flag not working as expected

- `--group` flag स्वचालित रूप से staged changes का विश्लेषण करता है और कई logical commits बना सकता है
- LLM यह तय कर सकता है कि आपके staged changes के सेट के लिए एकल कमिट समझ में आता है, भले ही `--group` के साथ हो
- यह जानबूझकर व्यवहार है - LLM logical relationships के आधार पर changes को ग्रुप करता है, केवल मात्रा के आधार पर नहीं
- सर्वोत्तम परिणामों के लिए सुनिश्चित करें कि आपके पास कई असंबंधित changes staged हैं (जैसे bug fix + feature addition)
- LLM क्या देख रहा है यह डीबग करने के लिए `gac --show-prompt` का उपयोग करें

**Problem:** Commits grouped incorrectly or not grouped when expected

- Grouping LLM के आपके changes के विश्लेषण द्वारा निर्धारित होती है
- LLM एकल कमिट बना सकता है यदि यह निर्धारित करता है कि changes logically related हैं
- Grouping logic को मार्गदर्शन देने के लिए `-h "hint"` के साथ hints जोड़ने का प्रयास करें (जैसे `-h "separate bug fix from refactoring"`)
- पुष्टि करने से पहले जेनरेट किए गए groups की समीक्षा करें
- यदि grouping आपके उपयोग के मामले के लिए अच्छा नहीं काम करता है, तो बजाय changes को अलग से कमिट करें

## 5. Security and Secret Detection

**Problem:** False positive: secret scan detects non-secrets

- Security scanner patterns की तलाश करता है जो API keys, tokens, और passwords से मिलते-जुलते हैं
- यदि आप placeholder keys के साथ example code, test fixtures, या documentation कमिट कर रहे हैं, तो आपको false positives दिखाई दे सकते हैं
- स्कैन को बायपास करने के लिए `--skip-secret-scan` का उपयोग करें यदि आप निश्चित हैं कि changes सुरक्षित हैं
- Test/example files को commits से बाहर करने पर विचार करें, या स्पष्ट रूप से चिह्नित placeholders का उपयोग करें

**Problem:** Secret scan not detecting actual secrets

- Scanner pattern matching का उपयोग करता है और सभी secret types को पकड़ नहीं सकता है
- हमेशा कमिट करने से पहले `git diff --staged` के साथ अपने staged changes की समीक्षा करें
- व्यापक सुरक्षा के लिए `git-secrets` या `gitleaks` जैसे अतिरिक्त security tools का उपयोग करने पर विचार करें
- Detection में सुधार करने में मदद करने के लिए कोई भी missed patterns को issues के रूप में रिपोर्ट करें

**Problem:** Need to disable secret scanning permanently

- अपनी `.gac.env` फाइल में `GAC_SKIP_SECRET_SCAN=true` सेट करें
- `gac config set GAC_SKIP_SECRET_SCAN true` का उपयोग करें
- नोट: केवल तभी अक्षम करें यदि आपके पास अन्य security measures हैं

## 6. Pre-commit and Lefthook Hook Issues

**Problem:** Pre-commit or lefthook hooks are failing and blocking commits

- सभी pre-commit और lefthook hooks को अस्थायी रूप से छोड़ने के लिए `gac --no-verify` का उपयोग करें
- Hooks को विफल करने वाले अंतर्निहित मुद्दों को ठीक करें
- यदि hooks बहुत सख्त हैं तो अपनी pre-commit या lefthook configuration को समायोजित करने पर विचार करें

**Problem:** Pre-commit or lefthook hooks take too long or are interfering with workflow

- सभी pre-commit और lefthook hooks को अस्थायी रूप से छोड़ने के लिए `gac --no-verify` का उपयोग करें
- अपने workflow के लिए `.pre-commit-config.yaml` में pre-commit hooks या `.lefthook.yml` में lefthook hooks को कम aggressive होने के लिए कॉन्फ़िगर करने पर विचार करें
- प्रदर्शन को अनुकूलित करने के लिए अपनी hook configuration की समीक्षा करें

## 7. Common Workflow Issues

**Problem:** No changes to commit / nothing staged

- gac को कमिट मैसेज जेनरेट करने के लिए staged changes की आवश्यकता होती है
- Changes को stage करने के लिए `git add <files>` का उपयोग करें, या सभी changes को स्वचालित रूप से stage करने के लिए `gac -a` का उपयोग करें
- संशोधित फाइलें देखने के लिए `git status` जांचें
- अपने changes का filtered view देखने के लिए `gac diff` का उपयोग करें

**Problem:** Commit message not what I expected

- इंटरैक्टिव feedback system का उपयोग करें: reroll के लिए `r` टाइप करें, edit के लिए `e`, या natural language feedback प्रदान करें
- LLM को मार्गदर्शन देने के लिए `-h "your hint"` के साथ context जोड़ें
- सरल one-line messages के लिए `-o` या अधिक detailed messages के लिए `-v` का उपयोग करें
- LLM को क्या जानकारी मिल रही है यह देखने के लिए `--show-prompt` का उपयोग करें

**Problem:** gac is too slow

- Confirmation prompt को छोड़ने के लिए `gac -y` का उपयोग करें
- कम output के साथ quiet mode के लिए `gac -q` का उपयोग करें
- नियमित commits के लिए तेज़/सस्ते मॉडल का उपयोग करने पर विचार करें
- यदि वे आपको धीमा कर रहे हैं तो hooks को छोड़ने के लिए `gac --no-verify` का उपयोग करें

**Problem:** Can't edit or provide feedback after message generation

- Prompt पर, edit mode में प्रवेश करने के लिए `e` टाइप करें (vi/emacs keybindings समर्थित)
- Feedback के बिना regenerate करने के लिए `r` टाइप करें
- या बस अपनी feedback सीधे टाइप करें (जैसे "make it shorter", "focus on the bug fix")
- प्रॉम्प्ट को फिर से देखने के लिए खाली input पर Enter दबाएं

## 8. General Debugging

- अपनी configuration को इंटरैक्टिव रूप से रीसेट या अपडेट करने के लिए `gac init` का उपयोग करें
- विस्तृत debug output और logging के लिए `gac --log-level=debug` का उपयोग करें
- LLM को कौन सा prompt भेजा जा रहा है यह देखने के लिए `gac --show-prompt` का उपयोग करें
- सभी उपलब्ध command-line flags देखने के लिए `gac --help` का उपयोग करें
- सभी वर्तमान configuration मान देखने के लिए `gac config show` का उपयोग करें
- Error messages और stack traces के लिए logs जांचें
- features, examples, और quick start instructions के लिए मुख्य [README.md](../../README.md) जांचें

## Still Stuck?

- मौजूदा issues खोजें या [GitHub repository](https://github.com/cellwebb/gac) पर एक नया issue खोलें
- अपने OS, Python version, gac version, provider, और error output के बारे में विवरण शामिल करें
- आप जितना अधिक विवरण प्रदान करते हैं, आपका issue उतना ही तेज़ी से हल किया जा सकता है

## Where to Get Further Help

- Features और usage examples के लिए, मुख्य [README.md](../../README.md) देखें
- Custom system prompts के लिए, [CUSTOM_SYSTEM_PROMPTS.md](../CUSTOM_SYSTEM_PROMPTS.md) देखें
- Contributing guidelines के लिए, [CONTRIBUTING.md](../CONTRIBUTING.md) देखें
- License information के लिए, [../../LICENSE](../../LICENSE) देखें
