LIBS=$(ls -1 lib/*.jar | tr '\n' ':')
export GRINDERHOME="/opt/grinder-3.11"
export CLASSPATH="lib:$LIBS$GRINDERHOME/lib/grinder.jar"
