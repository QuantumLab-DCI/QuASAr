pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                // Get some code from a GitHub repository
                sh 'docker build . -t "python-latest"'
            }
        }
        stage('Deploy') {
            steps{
            sh 'docker run -dit -v /var/run/docker.sock:/var/run/docker.sock -p 10000:10000 --name "python-jenkins" -d python-latest'
        }
        }
    }
}
