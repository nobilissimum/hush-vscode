file_name="hush-theme-$(jq -r '.version' package.json).vsix"
dir_path="dist"

mkdir -p "$dir_path"
mv "$file_name" "${dir_path}/${file_name}"
