pipeline {
    agent any

    environment {
        PYTHON_EXE = 'C:\\Users\\umram\\AppData\\Local\\Programs\\Python\\Python312\\python.exe'

        EC2_HOST = '3.110.212.222'

        DOCKER_IMAGE = 'umramahejabeen/invoice-tracker'

        GITHUB_REPO = 'https://github.com/Umramahejabeen/invoice-tracker.git'
    }

    stages {

        stage('Checkout SCM') {
            steps {
                checkout scm
            }
        }

        stage('Check Python') {
            steps {
                bat """
                "${PYTHON_EXE}" --version
                """
            }
        }

        stage('Create Virtual Environment') {
            steps {
                bat """
                if not exist venv (
                    "${PYTHON_EXE}" -m venv venv
                )
                """
            }
        }

        stage('Install Dependencies') {
            steps {
                bat '''
                venv\\Scripts\\python.exe -m pip install --upgrade pip
                venv\\Scripts\\python.exe -m pip install -r requirements.txt
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

        stage('Prepare EC2') {
            steps {
                withCredentials([
                    sshUserPrivateKey(
                        credentialsId: 'ec2-ssh-key',
                        keyFileVariable: 'SSH_KEY',
                        usernameVariable: 'SSH_USER'
                    )
                ]) {
                    bat '''
                    ssh -o StrictHostKeyChecking=no -i "%SSH_KEY%" %SSH_USER%@%EC2_HOST% "docker --version"
                    '''
                }
            }
        }

        stage('Clone Project on EC2') {
            steps {
                withCredentials([
                    sshUserPrivateKey(
                        credentialsId: 'ec2-ssh-key',
                        keyFileVariable: 'SSH_KEY',
                        usernameVariable: 'SSH_USER'
                    )
                ]) {
                    bat '''
                    ssh -o StrictHostKeyChecking=no -i "%SSH_KEY%" %SSH_USER%@%EC2_HOST% "rm -rf invoice-tracker && git clone %GITHUB_REPO% invoice-tracker"
                    '''
                }
            }
        }

        stage('Docker Hub Login') {
            steps {
                withCredentials([
                    sshUserPrivateKey(
                        credentialsId: 'ec2-ssh-key',
                        keyFileVariable: 'SSH_KEY',
                        usernameVariable: 'SSH_USER'
                    ),
                    usernamePassword(
                        credentialsId: 'dockerhub-creds',
                        usernameVariable: 'DOCKER_USER',
                        passwordVariable: 'DOCKER_PASS'
                    )
                ]) {
                    bat '''
                    ssh -o StrictHostKeyChecking=no -i "%SSH_KEY%" %SSH_USER%@%EC2_HOST% "docker login -u %DOCKER_USER% -p %DOCKER_PASS%"
                    '''
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                withCredentials([
                    sshUserPrivateKey(
                        credentialsId: 'ec2-ssh-key',
                        keyFileVariable: 'SSH_KEY',
                        usernameVariable: 'SSH_USER'
                    )
                ]) {
                    bat '''
                    ssh -o StrictHostKeyChecking=no -i "%SSH_KEY%" %SSH_USER%@%EC2_HOST% "cd invoice-tracker && docker build -t %DOCKER_IMAGE%:latest ."
                    '''
                }
            }
        }

        stage('Push Docker Image') {
            steps {
                withCredentials([
                    sshUserPrivateKey(
                        credentialsId: 'ec2-ssh-key',
                        keyFileVariable: 'SSH_KEY',
                        usernameVariable: 'SSH_USER'
                    )
                ]) {
                    bat '''
                    ssh -o StrictHostKeyChecking=no -i "%SSH_KEY%" %SSH_USER%@%EC2_HOST% "docker push %DOCKER_IMAGE%:latest"
                    '''
                }
            }
        }

        stage('Run Container') {
            steps {
                withCredentials([
                    sshUserPrivateKey(
                        credentialsId: 'ec2-ssh-key',
                        keyFileVariable: 'SSH_KEY',
                        usernameVariable: 'SSH_USER'
                    )
                ]) {
                    bat '''
                    ssh -o StrictHostKeyChecking=no -i "%SSH_KEY%" %SSH_USER%@%EC2_HOST% "docker rm -f invoice-tracker || true && docker run -d --name invoice-tracker -p 5000:5000 %DOCKER_IMAGE%:latest"
                    '''
                }
            }
        }

        stage('Check Container') {
            steps {
                withCredentials([
                    sshUserPrivateKey(
                        credentialsId: 'ec2-ssh-key',
                        keyFileVariable: 'SSH_KEY',
                        usernameVariable: 'SSH_USER'
                    )
                ]) {
                    bat '''
                    ssh -o StrictHostKeyChecking=no -i "%SSH_KEY%" %SSH_USER%@%EC2_HOST% "docker ps"
                    '''
                }
            }
        }
    }

    post {
        success {
            echo 'Invoice Tracker Jenkins Pipeline completed successfully!'
            echo 'Application deployed successfully on AWS EC2.'
        }

        failure {
            echo 'Pipeline FAILED. Check Jenkins Console Output.'
        }

        always {
            echo 'Invoice Tracker Jenkins Pipeline finished.'
        }
    }
}