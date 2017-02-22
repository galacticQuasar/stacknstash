import cx_Freeze

executables = [cx_Freeze.Executable("mainGame.py")]

cx_Freeze.setup(
    name="stash n' stack",
    options={"build_exe":{"packages":["pygame"],
                          "include_files":['sprites/','music/']}},
    executables = executables

    )
