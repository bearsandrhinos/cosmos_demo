pipeline {
    agent any
    stages {
        stage('Deploy to Astronomer') {
            when {
                expression {
                    return env.GIT_BRANCH == "origin/main"
                }
            }
            steps {
                checkout scm
                sh '''
                cat /etc/os-release
                uname -a
                curl -LJO https://github.com/astronomer/astro-cli/releases/download/v1.14.1/astro_1.14.1_linux_amd64.tar.gz
                tar -zxvf astro_1.14.1_linux_amd64.tar.gz astro && rm astro_1.14.1_linux_amd64.tar.gz
                ./astro deploy
                '''
            }
        }
    }
    post {
        always {
            cleanWs()
        }
    }
}