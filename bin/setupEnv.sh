LIBS=$(ls -1 lib/*.jar | tr '\n' ':')
export GRINDER_HOME="${GRINDER_HOME:-/opt/grinder-3.11}"
export CLASSPATH="lib:$LIBS$GRINDER_HOME/lib/grinder.jar"
