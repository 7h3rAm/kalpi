#!/usr/bin/env zsh

source $HOME/.zshrc

discord.sh "[`basename $0`] daily sync started"

python3 ${PROJECTSPATH}/kalpi/bitcoin.py

messages=$(cat $HOME/toolbox/bootstrap/commit_messages.txt)
num_messages=$(echo "$messages" | wc -l)
random_index=$[RANDOM % num_messages + 1]
msg=$(echo "$messages" | head -$random_index | tail -1)
emojis=( ⏳ ♻️ ⚗️ ⚡ ✅ ✨ ⬆️ ⬇️ ⭐ 🍎 🍒 🎉 🎨 🎵 🎶 🏁 🐎 🐗 🐛 🐞 🐧 🐳 🐻 👌 👍 👏 👕 👷 👽 💚 💡 💥 💪 💫 📅 📇 📍 📖 📚 📝 📦 📺 🔒 🔖 🔥 🔧 🔨 🗑️ 😆 😈 🙏 🚀 🚑 🚚 🚧 🚨 🤖 )
rand=$[$RANDOM % ${#emojis[@]}]
emj=$(echo ${emojis[$rand]})

cd ${PROJECTSPATH}/datastore && git status && git add . && git commit -m "${emj}  ${msg}" && git push -u

echo -en "bitcoin - last_update: " ; cat ${PROJECTSPATH}/datastore/bitcoin.json | jq '.last_update'

discord.sh "[`basename $0`] daily sync completed"
