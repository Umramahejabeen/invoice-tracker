pipeline {
    agent any

    environment {
        PYTHON_EXE = 'C:\\Users\\umram\\AppData\\Local\\Programs\\Python\\Python312\\python.exe'

        EC2_HOST = '13.206.204.208'

        DOCKER_IMAGE = 'umramahejabeen/invoice-tracker'

        DOCKER_CREDENTIALS = 'dockerhub-creds'

        EC2_CREDENTIALS = 'ec2-ssh-key'

        CONTAINER_NAME = 'invoice-tracker'

        APP_PORT = '5000'
    }

    stages {

        stage('Checkout SCM') {
            steps {
                echo '========================================'
                echo 'CHECKOUT SOURCE CODE'
                echo '========================================'

                checkout scm
            }
        }

        stage('Check Python') {
            steps {
                echo '========================================'
                echo 'CHECK PYTHON VERSION'
                echo '========================================'

                bat '"%PYTHON_EXE%" --version'
            }
        }

        stage('Create Virtual Environment') {
            steps {
                echo '========================================'
                echo 'CREATE PYTHON VIRTUAL ENVIRONMENT'
                echo '========================================'

                bat '''
                    if not exist venv (
                        "%PYTHON_EXE%" -m venv venv
                    )
                '''
            }
        }

        stage('Install Dependencies') {
            steps {
                echo '========================================'
                echo 'INSTALL PYTHON DEPENDENCIES'
                echo '========================================'

                bat '''
                    venv\\Scripts\\python.exe -m pip install --upgrade pip
                    venv\\Scripts\\python.exe -m pip install -r requirements.txt
                    venv\\Scripts\\python.exe -m pip install -r requirements-dev.txt
                '''
            }
        }

        stage('Lint') {
            steps {
                echo '========================================'
                echo 'RUN FLAKE8'
                echo '========================================'

                bat '''
                    venv\\Scripts\\python.exe -m flake8 app --max-line-length=120
                '''
            }
        }

        stage('Test') {
            steps {
                echo '========================================'
                echo 'RUN PYTEST'
                echo '========================================'

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
                echo '========================================'
                echo 'TEST EC2 SSH CONNECTION'
                echo '========================================'

                withCredentials([
                    sshUserPrivateKey(
                        credentialsId: "${EC2_CREDENTIALS}",
                        keyFileVariable: 'SSH_KEY',
                        usernameVariable: 'SSH_USER'
                    )
                ]) {

                    bat '''
                        echo Copying Jenkins SSH key...

                        copy /Y "%SSH_KEY%" "%WORKSPACE%\\jenkins-ec2-key.pem"

                        echo Fixing SSH key permissions...

                        icacls "%WORKSPACE%\\jenkins-ec2-key.pem" /inheritance:r

                        icacls "%WORKSPACE%\\jenkins-ec2-key.pem" /grant:r "SYSTEM:(R)"

                        icacls "%WORKSPACE%\\jenkins-ec2-key.pem" /grant:r "Administrators:(R)"

                        echo Testing SSH connection...

                        ssh -o StrictHostKeyChecking=no ^
                        -i "%WORKSPACE%\\jenkins-ec2-key.pem" ^
                        %SSH_USER%@%EC2_HOST% ^
                        "docker --version"
                    '''
                }
            }
        }

        stage('Clone Project on EC2') {
            steps {
                echo '========================================'
                echo 'CLONE PROJECT ON EC2'
                echo '========================================'

                withCredentials([
                    sshUserPrivateKey(
                        credentialsId: "${EC2_CREDENTIALS}",
                        keyFileVariable: 'SSH_KEY',
                        usernameVariable: 'SSH_USER'
                    )
                ]) {

                    bat '''
                        ssh -o StrictHostKeyChecking=no ^
                        -i "%WORKSPACE%\\jenkins-ec2-key.pem" ^
                        %SSH_USER%@%EC2_HOST% ^
                        "rm -rf ~/invoice-tracker && git clone https://github.com/Umramahejabeen/invoice-tracker.git ~/invoice-tracker"
                    '''
                }
            }
        }

        stage('Docker Hub Login') {
            steps {
                echo '========================================'
                echo 'DOCKER HUB LOGIN ON EC2'
                echo '========================================'

                withCredentials([

                    usernamePassword(
                        credentialsId: "${DOCKER_CREDENTIALS}",
                        usernameVariable: 'DOCKER_USERNAME',
                        passwordVariable: 'DOCKER_PASSWORD'
                    ),

                    sshUserPrivateKey(
                        credentialsId: "${EC2_CREDENTIALS}",
                        keyFileVariable: 'SSH_KEY',
                        usernameVariable: 'SSH_USER'
                    )

                ]) {

                    bat '''
                        echo Logging in to Docker Hub on EC2...

                        echo %DOCKER_PASSWORD% | ssh ^
                        -o StrictHostKeyChecking=no ^
                        -i "%WORKSPACE%\\jenkins-ec2-key.pem" ^
                        %SSH_USER%@%EC2_HOST% ^
                        "docker login --username %DOCKER_USERNAME% --password-stdin"

                        if errorlevel 1 (
                            echo Docker Hub login failed
                            exit /b 1
                        )

                        echo Docker Hub login successful
                    '''
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                echo '========================================'
                echo 'BUILD DOCKER IMAGE ON EC2'
                echo '========================================'

                withCredentials([
                    sshUserPrivateKey(
                        credentialsId: "${EC2_CREDENTIALS}",
                        keyFileVariable: 'SSH_KEY',
                        usernameVariable: 'SSH_USER'
                    )
                ]) {

                    bat '''
                        ssh -o StrictHostKeyChecking=no ^
                        -i "%WORKSPACE%\\jenkins-ec2-key.pem" ^
                        %SSH_USER%@%EC2_HOST% ^
                        "cd ~/invoice-tracker && docker build -t %DOCKER_IMAGE%:latest ."
                    '''
                }
            }
        }

        stage('Push Docker Image') {
            steps {
                echo '========================================'
                echo 'PUSH IMAGE TO DOCKER HUB'
                echo '========================================'

                withCredentials([
                    sshUserPrivateKey(
                        credentialsId: "${EC2_CREDENTIALS}",
                        keyFileVariable: 'SSH_KEY',
                        usernameVariable: 'SSH_USER'
                    )
                ]) {

                    bat '''
                        ssh -o StrictHostKeyChecking=no ^
                        -i "%WORKSPACE%\\jenkins-ec2-key.pem" ^
                        %SSH_USER%@%EC2_HOST% ^
                        "docker push %DOCKER_IMAGE%:latest"
                    '''
                }
            }
        }

        stage('Run Container') {
            steps {
                echo '========================================'
                echo 'RUN FLASK CONTAINER'
                echo '========================================'

                withCredentials([
                    sshUserPrivateKey(
                        credentialsId: "${EC2_CREDENTIALS}",
                        keyFileVariable: 'SSH_KEY',
                        usernameVariable: 'SSH_USER'
                    )
                ]) {

                    bat '''
                        ssh -o StrictHostKeyChecking=no ^
                        -i "%WORKSPACE%\\jenkins-ec2-key.pem" ^
                        %SSH_USER%@%EC2_HOST% ^
                        "docker rm -f %CONTAINER_NAME% 2>/dev/null || true && docker run -d --name %CONTAINER_NAME% --restart unless-stopped -p %APP_PORT%:%APP_PORT% %DOCKER_IMAGE%:latest"
                    '''
                }
            }
        }

        stage('Check Container') {
            steps {
                echo '========================================'
                echo 'CHECK CONTAINER'
                echo '========================================'

                withCredentials([
                    sshUserPrivateKey(
                        credentialsId: "${EC2_CREDENTIALS}",
                        keyFileVariable: 'SSH_KEY',
                        usernameVariable: 'SSH_USER'
                    )
                ]) {

                    bat '''
                        ssh -o StrictHostKeyChecking=no ^
                        -i "%WORKSPACE%\\jenkins-ec2-key.pem" ^
                        %SSH_USER%@%EC2_HOST% ^
                        "docker ps --filter name=%CONTAINER_NAME%"
                    '''
                }
            }
        }

        stage('Health Check') {
            steps {
                echo '========================================'
                echo 'APPLICATION HEALTH CHECK'
                echo '========================================'

                withCredentials([
                    sshUserPrivateKey(
                        credentialsId: "${EC2_CREDENTIALS}",
                        keyFileVariable: 'SSH_KEY',
                        usernameVariable: 'SSH_USER'
                    )
                ]) {

                    bat '''
                        ssh -o StrictHostKeyChecking=no ^
                        -i "%WORKSPACE%\\jenkins-ec2-key.pem" ^
                        %SSH_USER%@%EC2_HOST% ^
                        "sleep 10 && curl -f http://localhost:%APP_PORT%/health"
                    '''
                }
            }
        }
    }

    post {

        success {
            echo '========================================'
            echo 'PIPELINE SUCCESS'
            echo '========================================'

            echo 'Invoice Tracker deployed successfully.'

            echo 'Application URL:'

            echo "http://${EC2_HOST}:${APP_PORT}/health"
        }

        failure {
            echo '========================================'
            echo 'PIPELINE FAILED'
            echo 'Check Jenkins Console Output'
            echo '========================================'
        }

        always {
            echo 'Cleaning temporary SSH key...'

            bat '''
                if exist "%WORKSPACE%\\jenkins-ec2-key.pem" (
                    del /F /Q "%WORKSPACE%\\jenkins-ec2-key.pem"
                )
            '''

            echo 'Invoice Tracker Jenkins Pipeline finished.'
        }
    }
}