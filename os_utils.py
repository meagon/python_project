

def execute_command(cmd):

    """
      given a command
      return output_status, and out_data
    """

    execute_state=False
    stdoutdata=None
    stderrdata=None
    try:
        child_process=subprocess.Popen(cmd, shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        out_data, err_status = child_process.communicate()
        if out_data != None:
            execute_state=True
    except Exception, err:
            logger.error("subprocess  execute_command() error" + str(err))
            print(str(err))
    return execute_state,out_data


