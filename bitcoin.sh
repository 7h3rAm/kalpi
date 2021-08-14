#!/usr/bin/env zsh

source /home/shiv/.zshrc

python3 /run/media/shiv/1tb/shared/projects/kalpi/bitcoin.py

messages=$(cat /home/shiv/toolbox/bootstrap/commit_messages.txt)
num_messages=$(echo "$messages" | wc -l)
random_index=$[RANDOM % num_messages + 1]
msg=$(echo "$messages" | head -$random_index | tail -1)
emojis=( ⏳ ♻️ ⚗️ ⚡ ✅ ✨ ⬆️ ⬇️ ⭐ 🍎 🍒 🎉 🎨 🎵 🎶 🏁 🐎 🐗 🐛 🐞 🐧 🐳 🐻 👌 👍 👏 👕 👷 👽 💚 💡 💥 💪 💫 📅 📇 📍 📖 📚 📝 📦 📺 🔒 🔖 🔥 🔧 🔨 🗑️ 😆 😈 🙏 🚀 🚑 🚚 🚧 🚨 🤖 )
rand=$[$RANDOM % ${#emojis[@]}]
emj=$(echo ${emojis[$rand]})

cd /run/media/shiv/1tb/shared/projects/datastore && git status && git add . && git commit -m "${emj}  ${msg}" && git push -u

echo -en "bitcoin - last_update: " ; cat /run/media/shiv/1tb/shared/projects/datastore/bitcoin.json | jq '.last_update'
