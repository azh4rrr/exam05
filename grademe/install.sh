#!/bin/sh
# Installs the `examshell` command by symlinking it into a directory of your PATH.
set -e
SRC="$(cd "$(dirname "$0")" && pwd)/examshell"
chmod +x "$SRC"

for dir in /usr/local/bin /opt/homebrew/bin "$HOME/.local/bin" "$HOME/bin"; do
	case ":$PATH:" in *":$dir:"*) ;; *) continue ;; esac
	if [ -d "$dir" ] && [ -w "$dir" ]; then
		ln -sf "$SRC" "$dir/examshell"
		echo "Installed: $dir/examshell -> $SRC"
		echo "Run 'examshell' from any folder to start an exam."
		exit 0
	fi
done

mkdir -p "$HOME/.local/bin"
ln -sf "$SRC" "$HOME/.local/bin/examshell"
echo "Installed: $HOME/.local/bin/examshell -> $SRC"
echo "That folder is not in your PATH yet. Add this line to your ~/.zshrc (or ~/.bashrc):"
echo '    export PATH="$HOME/.local/bin:$PATH"'
echo "then open a new terminal and run 'examshell'."
