pipeline {
    agent any

    environment {
        PYTHON = 'C:\\Users\\umram\\AppData\\Local\\Programs\\Python\\Python312\\python.exe'

        DOCKER_IMAGE = 'umramahejabeen/invoice-tracker'
        EC2_HOST = '3.110.212.222'
        EC2_USER = 'ec2-user'
    }

    stages {

        stage('Checkout SCM') {
            steps {
                checkout scm
            }
        }

        stage('Create Virtual Environment') {
            steps {
                bat '''
                if not exist venv (
                    "%PYTHON%" -m venv venv
                )
                '''
            }
        }

        stage('Install Dependencies') {
            steps {
                bat '''
                venv\\Scripts\\python.exe -m pip install --upgrade pip
                venv\\Scripts\\python.exe -m pip install -r requirements-dev.txt
                '''
            }
        }

        stage('Lint') {
            steps {
                bat '''
                venv\\Scripts\\python.exe -m flake8 app --max-line-length=120
                '''
            }
        }

        stage('Test') {
            steps {
                bat '''
                venv\\Scripts\\python.exe -m pytest --junitxml=test-results.xml
                '''
            }

            post {
                always {
                    junit allowEmptyResults: true,
                          testResults: 'test-results.xml'
                }
            }
        }

        stage('Deploy to EC2') {
            steps {
                sshagent(credentials: ['ec2-ssh-key']) {

                    bat '''
                    ssh -o StrictHostKeyChecking=no %EC2_USER%@%EC2_HOST% "rm -rf invoice-tracker && git clone https://github.com/Umramahejabeen/invoice-tracker.git"
                    '''

                    bat '''
                    ssh -o StrictHostKeyChecking=no %EC2_USER%@%EC2_HOST% "cd invoice-tracker && sudo docker build -t %DOCKER_IMAGE%:latest ."
                    '''
                }
            }
        }

        stage('Docker Hub Login') {
            steps {
                sshagent(credentials: ['ec2-ssh-key']) {

                    withCredentials([
                        usernamePassword(
                            credentialsId: 'dockerhub-creds',
                            usernameVariable: 'DOCKER_USER',
                            passwordVariable: 'DOCKER_PASSWORD'
                        )
                    ]) {

                        bat '''
                        echo %DOCKER_PASSWORD% | ssh -o StrictHostKeyChecking=no %EC2_USER%@%EC2_HOST% "sudo docker login -u %DOCKER_USER% --password-stdin"
                        '''

                    }
                }
            }
        }

        stage('Push Docker Image') {
            steps {
                sshagent(credentials: ['ec2-ssh-key']) {

                    bat '''
                    ssh -o StrictHostKeyChecking=no %EC2_USER%@%EC2_HOST% "sudo docker push %DOCKER_IMAGE%:latest"
                    '''

                }
            }
        }

        stage('Run Container') {
            steps {
                sshagent(credentials: ['ec2-ssh-key']) {

                    bat '''
                    ssh -o StrictHostKeyChecking=no %EC2_USER%@%EC2_HOST% "sudo docker rm -f invoice-tracker || true"
                    '''

                    bat '''
                    ssh -o StrictHostKeyChecking=no %EC2_USER%@%EC2_HOST% "sudo docker run -d --name invoice-tracker -p 5000:5000 %DOCKER_IMAGE%:latest"
                    '''

                }
            }
        }
    }

    post {

        success {
            echo 'Invoice Tracker CI/CD Pipeline SUCCESS'
            echo 'Application deployed successfully to AWS EC2'
        }

        failure {
            echo 'Pipeline FAILED. Check Console Output.'
        }

        always {
            echo 'Invoice Tracker Jenkins Pipeline finished.'
        }
    }
}