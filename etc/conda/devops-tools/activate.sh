function cd() {
    
    builtin cd "$@"

    export GIT_DESCRIBE_VERSION=`git_describe_version`
    export GIT_DESCRIBE_NUMBER=`git_describe_number`

    export DATETIME_DESCRIBE_VERSION=`datetime_describe_version`
    export DATETIME_DESCRIBE_NUMBER=`datetime_describe_number`
}