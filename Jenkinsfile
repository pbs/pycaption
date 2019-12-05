@Library('zefrSharedLibraries') _

//parameter here: language
//  can be one of: python, kotlin, java, scala
def paramList = parameterSetup("python")

additionalParams = []

properties([
  parameters(paramList + additionalParams)
])

standardPythonPipeline {
    projectName        = "pycaption"
    slackChannel       = "rightsid-services"
}