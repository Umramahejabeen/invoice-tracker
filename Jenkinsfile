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
                    icacls "%SSH_KEY%" /inheritance:r
                    icacls "%SSH_KEY%" /remove "BUILTIN\\Users"
                    icacls "%SSH_KEY%" /remove "Authenticated Users"
                    icacls "%SSH_KEY%" /remove "Everyone"
                    icacls "%SSH_KEY%" /grant:r "%USERNAME%:R"

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
                    icacls "%SSH_KEY%" /inheritance:r
                    icacls "%SSH_KEY%" /remove "BUILTIN\\Users"
                    icacls "%SSH_KEY%" /remove "Authenticated Users"
                    icacls "%SSH_KEY%" /remove "Everyone"
                    icacls "%SSH_KEY%" /grant:r "%USERNAME%:R"

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
                    icacls "%SSH_KEY%" /inheritance:r
                    icacls "%SSH_KEY%" /remove "BUILTIN\\Users"
                    icacls "%SSH_KEY%" /remove "Authenticated Users"
                    icacls "%SSH_KEY%" /remove "Everyone"
                    icacls "%SSH_KEY%" /grant:r "%USERNAME%:R"

                    echo %DOCKER_PASS% | ssh -o StrictHostKeyChecking=no -i "%SSH_KEY%" %SSH_USER%@%EC2_HOST% "docker login -u %DOCKER_USER% --password-stdin"
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
                    icacls "%SSH_KEY%" /inheritance:r
                    icacls "%SSH_KEY%" /remove "BUILTIN\\Users"
                    icacls "%SSH_KEY%" /remove "Authenticated Users"
                    icacls "%SSH_KEY%" /remove "Everyone"
                    icacls "%SSH_KEY%" /grant:r "%USERNAME%:R"

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
                    icacls "%SSH_KEY%" /inheritance:r
                    icacls "%SSH_KEY%" /remove "BUILTIN\\Users"
                    icacls "%SSH_KEY%" /remove "Authenticated Users"
                    icacls "%SSH_KEY%" /remove "Everyone"
                    icacls "%SSH_KEY%" /grant:r "%USERNAME%:R"

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
                    icacls "%SSH_KEY%" /inheritance:r
                    icacls "%SSH_KEY%" /remove "BUILTIN\\Users"
                    icacls "%SSH_KEY%" /remove "Authenticated Users"
                    icacls "%SSH_KEY%" /remove "Everyone"
                    icacls "%SSH_KEY%" /grant:r "%USERNAME%:R"

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
                    icacls "%SSH_KEY%" /inheritance:r
                    icacls "%SSH_KEY%" /remove "BUILTIN\\Users"
                    icacls "%SSH_KEY%" /remove "Authenticated Users"
                    icacls "%SSH_KEY%" /remove "Everyone"
                    icacls "%SSH_KEY%" /grant:r "%USERNAME%:R"

                    ssh -o StrictHostKeyChecking=no -i "%SSH_KEY%" %SSH_USER%@%EC2_HOST% "docker ps && docker logs invoice-tracker"
                    '''
                }
            }
        }

        stage('Health Check') {
            steps {
                withCredentials([
                    sshUserPrivateKey(
                        credentialsId: 'ec2-ssh-key',
                        keyFileVariable: 'SSH_KEY',
                        usernameVariable: 'SSH_USER'
                    )
                ]) {
                    bat '''
                    icacls "%SSH_KEY%" /inheritance:r
                    icacls "%SSH_KEY%" /remove "BUILTIN\\Users"
                    icacls "%SSH_KEY%" /remove "Authenticated Users"
                    icacls "%SSH_KEY%" /remove "Everyone"
                    icacls "%SSH_KEY%" /grant:r "%USERNAME%:R"

                    ssh -o StrictHostKeyChecking=no -i "%SSH_KEY%" %SSH_USER%@%EC2_HOST% "sleep 5 && curl -f http://localhost:5000/health"
                    '''
                }
            }
        }
    }

    post {
        success {
            echo '========================================='
            echo 'PIPELINE SUCCESSFUL'
            echo 'Invoice Tracker deployed on AWS EC2'
            echo 'Docker image pushed to Docker Hub'
            echo '========================================='
        }

        failure {
            echo '========================================='
            echo 'PIPELINE FAILED'
            echo 'Check Jenkins Console Output'
            echo '========================================='
        }

        always {
            echo 'Invoice Tracker Jenkins Pipeline finished.'
        }
    }
}