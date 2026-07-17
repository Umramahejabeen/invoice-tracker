pipeline {

    agent any

    environment {
        PYTHON_EXE = 'C:\\Users\\umram\\AppData\\Local\\Programs\\Python\\Python312\\python.exe'

        EC2_HOST = '3.110.81.211'
        EC2_CREDENTIALS = 'ec2-ssh-key'

        DOCKER_CREDENTIALS = 'dockerhub-creds'
        DOCKER_USERNAME = 'umramahejabeen'

        IMAGE_NAME = 'umramahejabeen/invoice-tracker'
        CONTAINER_NAME = 'invoice-tracker'

        APP_PORT = '5000'
    }

    stages {

        stage('Checkout SCM') {
            steps {
                echo '========================================'
                echo 'CHECKOUT PROJECT'
                echo '========================================'

                checkout scm
            }
        }

        stage('Check Python') {
            steps {
                echo '========================================'
                echo 'CHECK PYTHON'
                echo '========================================'

                bat '''
                    "%PYTHON_EXE%" --version

                    if errorlevel 1 (
                        echo Python check failed
                        exit /b 1
                    )

                    echo Python detected successfully
                '''
            }
        }

        stage('Create Virtual Environment') {
            steps {
                echo '========================================'
                echo 'CREATE VIRTUAL ENVIRONMENT'
                echo '========================================'

                bat '''
                    if exist venv (
                        echo Removing old virtual environment...
                        rmdir /S /Q venv
                    )

                    "%PYTHON_EXE%" -m venv venv

                    if errorlevel 1 (
                        echo Virtual environment creation failed
                        exit /b 1
                    )

                    echo Virtual environment created successfully
                '''
            }
        }

        stage('Install Dependencies') {
            steps {
                echo '========================================'
                echo 'INSTALL DEPENDENCIES'
                echo '========================================'

                bat '''
                    venv\\Scripts\\python.exe -m pip install --upgrade pip

                    venv\\Scripts\\python.exe -m pip install -r requirements.txt

                    if exist requirements-dev.txt (
                        venv\\Scripts\\python.exe -m pip install -r requirements-dev.txt
                    )

                    echo Dependencies installed successfully
                '''
            }
        }

        stage('Lint') {
            steps {
                echo '========================================'
                echo 'RUN PYTHON LINT'
                echo '========================================'

                bat '''
                    venv\\Scripts\\python.exe -m flake8 app tests --max-line-length=120

                    if errorlevel 1 (
                        echo Lint failed
                        exit /b 1
                    )

                    echo Lint passed successfully
                '''
            }
        }

        stage('Test') {
            steps {
                echo '========================================'
                echo 'RUN PYTHON TESTS'
                echo '========================================'

                bat '''
                    venv\\Scripts\\python.exe -m pytest -v

                    if errorlevel 1 (
                        echo Tests failed
                        exit /b 1
                    )

                    echo Tests passed successfully
                '''
            }
        }

        stage('Prepare EC2') {
            steps {
                echo '========================================'
                echo 'PREPARE EC2'
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

                        icacls "%WORKSPACE%\\jenkins-ec2-key.pem" /inheritance:r

                        icacls "%WORKSPACE%\\jenkins-ec2-key.pem" /grant:r "SYSTEM:(R)"

                        icacls "%WORKSPACE%\\jenkins-ec2-key.pem" /grant:r "Administrators:(R)"

                        echo Testing EC2 connection...

                        ssh -o StrictHostKeyChecking=no ^
                        -i "%WORKSPACE%\\jenkins-ec2-key.pem" ^
                        %SSH_USER%@%EC2_HOST% ^
                        "echo EC2 CONNECTION SUCCESSFUL && docker --version"

                        if errorlevel 1 (
                            echo EC2 connection failed
                            exit /b 1
                        )

                        echo EC2 is ready
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

                        if errorlevel 1 (
                            echo Project clone failed
                            exit /b 1
                        )

                        echo Project cloned successfully
                    '''
                }
            }
        }

        stage('Check Docker') {
            steps {
                echo '========================================'
                echo 'CHECK DOCKER ON EC2'
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
                        "docker --version && docker info > /dev/null"

                        if errorlevel 1 (
                            echo Docker is not available on EC2
                            exit /b 1
                        )

                        echo Docker is running on EC2
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
                        "cd ~/invoice-tracker && docker build -t %IMAGE_NAME%:latest ."

                        if errorlevel 1 (
                            echo Docker image build failed
                            exit /b 1
                        )

                        echo Docker image built successfully
                    '''
                }
            }
        }

        stage('Push Docker Image') {
    steps {

        echo '========================================'
        echo 'LOGIN AND PUSH DOCKER IMAGE'
        echo '========================================'

        withCredentials([

            usernamePassword(
                credentialsId: "${DOCKER_CREDENTIALS}",
                usernameVariable: 'DOCKER_USER',
                passwordVariable: 'DOCKER_TOKEN'
            ),

            sshUserPrivateKey(
                credentialsId: "${EC2_CREDENTIALS}",
                keyFileVariable: 'SSH_KEY',
                usernameVariable: 'SSH_USER'
            )

        ]) {

            bat '''
copy /Y "%SSH_KEY%" "%WORKSPACE%\\jenkins-ec2-key.pem"

ssh -o StrictHostKeyChecking=no ^
-i "%WORKSPACE%\\jenkins-ec2-key.pem" ^
%SSH_USER%@%EC2_HOST% ^
"echo '%DOCKER_TOKEN%' | docker login -u %DOCKER_USER% --password-stdin && docker push %IMAGE_NAME%:latest"

if errorlevel 1 (
    echo Docker push failed
    exit /b 1
)

echo Docker image pushed successfully
'''
        }
    }
}

        stage('Run Container') {
            steps {
                echo '========================================'
                echo 'RUN CONTAINER ON EC2'
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
                    "docker rm -f invoice-tracker >/dev/null 2>&1; docker run -d --name invoice-tracker -p 5000:5000 umramahejabeen/invoice-tracker:latest"

                        if errorlevel 1 (
                            echo Container deployment failed
                            exit /b 1
                        )

                        echo Container started successfully
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

                        if errorlevel 1 (
                            echo Container check failed
                            exit /b 1
                        )

                        echo Container is running
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
                        echo Waiting for application startup...

                        timeout /T 10 /NOBREAK

                        ssh -o StrictHostKeyChecking=no ^
                        -i "%WORKSPACE%\\jenkins-ec2-key.pem" ^
                        %SSH_USER%@%EC2_HOST% ^
                        "curl -f http://localhost:%APP_PORT%/health"

                        if errorlevel 1 (
                            echo Application health check failed
                            exit /b 1
                        )

                        echo Application is healthy
                    '''
                }
            }
        }
    }

    post {

        success {
            echo '========================================'
            echo 'PIPELINE SUCCESSFUL'
            echo '========================================'
            echo 'Invoice Tracker deployed successfully'
            echo "EC2 Server: ${EC2_HOST}"
            echo "Docker Image: ${IMAGE_NAME}:latest"
        }

        failure {
            echo '========================================'
            echo 'PIPELINE FAILED'
            echo '========================================'
            echo 'Check the failed Jenkins stage'
        }

        always {
            echo 'Cleaning Jenkins workspace temporary SSH key...'

            bat '''
                if exist "%WORKSPACE%\\jenkins-ec2-key.pem" (
                    del /F /Q "%WORKSPACE%\\jenkins-ec2-key.pem"
                )
            '''
        }
    }
}