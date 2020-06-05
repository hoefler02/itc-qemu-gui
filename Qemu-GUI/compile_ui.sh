#! /bin/bash
# note that this expects the python virtual environment to be active and should be called from the project root

repo_root=$(pwd)

# compile the ui files
cd ./qemu_gui/ui

echo "================      Compiling UI Files      ================"
for entry in *.ui
do
  name=${entry%.ui}  # strip .ui from the entry text
  name="${name}_ui"
  pyside2-uic -o "./compiled/${name}.py" "$entry"
  echo "$entry --> ./compiled/${name}.py" 
done
echo "================    Compiling Resource File   ================"

# compile the resouces file, then silence pylint
pyside2-rcc ./resources/resources.qrc -o ./compiled/resources_rc.py
sed -i '1s/^/# pylint: skip-file\n/' ./compiled/resources_rc.py
echo "./resources/resources.qrc --> ./compiled/resources_rc.py"

echo "================ Fixing Resoure Import Issues ================"
# fix the import issues and silence pylint
cd ./compiled
for entry in ./*ui*.py
do
  sed -i '1s/^/# pylint: skip-file\n/' "${entry}"
  sed -i 's/import resources_rc/from ui.compiled import resources_rc/g' "${entry}"
done

# we are done, go back to repo root
cd "$repo_root"
echo "================     Compilation Complete     ================"
