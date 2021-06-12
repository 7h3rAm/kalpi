#!/usr/bin/env zsh

source /home/shiv/.zshrc

/home/shiv/toolbox/scripts/speak.sh "Starting astro hourly cron job"

python3 /run/media/shiv/1tb/shared/projects/kalpi/astro.py

messages=$(cat /home/shiv/toolbox/bootstrap/commit_messages.txt)
num_messages=$(echo "$messages" | wc -l)
random_index=$[RANDOM % num_messages + 1]
msg=$(echo "$messages" | head -$random_index | tail -1)

emojis=( ⏳ ♻️ ⚗️ ⚡ ✅ ✨ ⬆️ ⬇️ ⭐ 🍎 🍒 🎉 🎨 🎵 🎶 🏁 🐎 🐗 🐛 🐞 🐧 🐳 🐻 👌 👍 👏 👕 👷 👽 💚 💡 💥 💪 💫 📅 📇 📍 📖 📚 📝 📦 📺 🔒 🔖 🔥 🔧 🔨 🗑️ 😆 😈 🙏 🚀 🚑 🚚 🚧 🚨 🤖 )
rand=$[$RANDOM % ${#emojis[@]}]
emj=$(echo ${emojis[$rand]})

cd /run/media/shiv/1tb/shared/projects/datastore && git status && git add . && git commit -m "${emj}  ${msg}" && git push -u

cat /run/media/shiv/1tb/shared/projects/datastore/astro.json | jq '.last_update'

/home/shiv/toolbox/scripts/speak.sh "Finished astro hourly cron job"
