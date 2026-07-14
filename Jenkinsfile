pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'invoice-tracker'
        DOCKER_REPO = 'umramahejabeen/invoice-tracker'
    }

    stages {

        stage('Install Dependencies') {
            steps {
                bat 'venv\\Scripts\\python -m pip install -r requirements-dev.txt'
            }
        }

        stage('Lint') {
            steps {
                bat 'venv\\Scripts\\python -m flake8 app --max-line-length=120'
            }
        }

        stage('Test') {
            steps {
                bat 'venv\\Scripts\\python -m pytest tests -v --junitxml=test-results.xml'
            }

            post {
                always {
                    junit 'test-results.xml'
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                bat 'docker build -t %DOCKER_IMAGE%:latest .'
            }
        }

        stage('Push Docker Image') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub-creds',
                        usernameVariable: 'DOCKER_USER',
                        passwordVariable: 'DOCKER_PASS'
                    )
                ]) {
                    bat '''
                        echo %DOCKER_PASS% | docker login -u %DOCKER_USER% --password-stdin
                        docker tag %DOCKER_IMAGE%:latest %DOCKER_REPO%:latest
                        docker push %DOCKER_REPO%:latest
                    '''
                }
            }
        }
    }

    post {
        success {
            echo 'CI Pipeline completed successfully!'
            echo 'Docker image pushed to Docker Hub.'
        }

        failure {
            echo 'Pipeline failed. Check the Jenkins Console Output.'
        }

        always {
            echo 'Invoice Tracker Jenkins Pipeline finished.'
        }
    }
}