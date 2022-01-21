#!/usr/bin/env zsh

source $HOME/.zshrc

discord.sh "[`basename $0`] hourly sync started"

python3 ${PROJECTSPATH}/kalpi/astro.py

messages=$(cat $HOME/toolbox/bootstrap/commit_messages.txt)
num_messages=$(echo "$messages" | wc -l)
random_index=$[RANDOM % num_messages + 1]
msg=$(echo "$messages" | head -$random_index | tail -1)
emojis=( ⏳ ♻️ ⚗️ ⚡ ✅ ✨ ⬆️ ⬇️ ⭐ 🍎 🍒 🎉 🎨 🎵 🎶 🏁 🐎 🐗 🐛 🐞 🐧 🐳 🐻 👌 👍 👏 👕 👷 👽 💚 💡 💥 💪 💫 📅 📇 📍 📖 📚 📝 📦 📺 🔒 🔖 🔥 🔧 🔨 🗑️ 😆 😈 🙏 🚀 🚑 🚚 🚧 🚨 🤖 )
rand=$[$RANDOM % ${#emojis[@]}]
emj=$(echo ${emojis[$rand]})

cd ${PROJECTSPATH}/datastore && git status && git add . && git commit -m "${emj}  ${msg}" && git push -u

echo -en "astro - last_update: " ; cat ${PROJECTSPATH}/datastore/astro.json | jq '.last_update'

discord.sh "[`basename $0`] hourly sync completed"
