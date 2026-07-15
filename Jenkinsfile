pipeline {

    agent any

    environment {

        // ========================================
        // GITHUB CONFIGURATION
        // ========================================

        GIT_REPO = 'https://github.com/Umramahejabeen/invoice-tracker.git'
        GIT_BRANCH = 'main'


        // ========================================
        // EC2 CONFIGURATION
        // ========================================

        EC2_HOST = '13.206.204.208'
        EC2_CREDENTIALS = 'ec2-ssh-key'


        // ========================================
        // DOCKER CONFIGURATION
        // ========================================

        DOCKER_IMAGE = 'umramahejabeen/invoice-tracker'

        IMAGE_TAG = "${BUILD_NUMBER}"


        // ========================================
        // APPLICATION CONFIGURATION
        // ========================================

        CONTAINER_NAME = 'invoice-tracker'

        APP_PORT = '5000'

        HOST_PORT = '5000'
    }


    stages {


        // ==================================================
        // CHECKOUT SOURCE CODE
        // ==================================================

        stage('Checkout SCM') {

            steps {

                echo '========================================'

                echo 'CHECKOUT SOURCE CODE'

                echo '========================================'


                checkout scm
            }
        }



        // ==================================================
        // CHECK PYTHON
        // ==================================================

        stage('Check Python') {

            steps {

                echo '========================================'

                echo 'CHECK PYTHON'

                echo '========================================'


                bat '''

                    py --version

                    if errorlevel 1 (

                        echo Python is not available

                        exit /b 1

                    )

                    echo Python detected successfully

                '''
            }
        }



        // ==================================================
        // CREATE VIRTUAL ENVIRONMENT
        // ==================================================

        stage('Create Virtual Environment') {

            steps {

                echo '========================================'

                echo 'CREATE PYTHON VIRTUAL ENVIRONMENT'

                echo '========================================'


                bat '''

                    if exist venv (

                        echo Removing existing virtual environment...

                        rmdir /S /Q venv

                    )


                    echo Creating virtual environment...


                    py -m venv venv


                    if errorlevel 1 (

                        echo Virtual environment creation failed

                        exit /b 1

                    )


                    echo Virtual environment created successfully

                '''
            }
        }



        // ==================================================
        // INSTALL DEPENDENCIES
        // ==================================================

        stage('Install Dependencies') {

            steps {

                echo '========================================'

                echo 'INSTALL PYTHON DEPENDENCIES'

                echo '========================================'


                bat '''

                    venv\\Scripts\\python.exe -m pip install --upgrade pip


                    venv\\Scripts\\python.exe -m pip install -r requirements.txt


                    if exist requirements-dev.txt (

                        venv\\Scripts\\python.exe -m pip install -r requirements-dev.txt

                    )


                    if errorlevel 1 (

                        echo Dependency installation failed

                        exit /b 1

                    )


                    echo Dependencies installed successfully

                '''
            }
        }



        // ==================================================
        // PYTHON LINT
        // ==================================================

        stage('Lint') {

            steps {

                echo '========================================'

                echo 'RUN PYTHON LINT'

                echo '========================================'


                bat '''

                    venv\\Scripts\\python.exe -m flake8 app tests --max-line-length=120


                    if errorlevel 1 (

                        echo Python lint failed

                        exit /b 1

                    )


                    echo Python lint successful

                '''
            }
        }



        // ==================================================
        // RUN PYTHON TESTS
        // ==================================================

        stage('Test') {

            steps {

                echo '========================================'

                echo 'RUN PYTHON TESTS'

                echo '========================================'


                bat '''

                    venv\\Scripts\\python.exe -m pytest -v


                    if errorlevel 1 (

                        echo Python tests failed

                        exit /b 1

                    )


                    echo All tests passed

                '''
            }
        }



        // ==================================================
        // PREPARE EC2
        // ==================================================

        stage('Prepare EC2') {

            steps {

                echo '========================================'

                echo 'PREPARE EC2 SERVER'

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


                        echo Testing SSH connection to EC2...


                        ssh ^

                        -o StrictHostKeyChecking=no ^

                        -i "%WORKSPACE%\\jenkins-ec2-key.pem" ^

                        %SSH_USER%@%EC2_HOST% ^

                        "echo EC2 CONNECTED && docker --version"


                        if errorlevel 1 (

                            echo EC2 SSH connection failed

                            exit /b 1

                        )


                        echo EC2 connection successful

                    '''
                }
            }
        }



        // ==================================================
        // CLONE PROJECT ON EC2
        // ==================================================

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

                        ssh ^

                        -o StrictHostKeyChecking=no ^

                        -i "%WORKSPACE%\\jenkins-ec2-key.pem" ^

                        %SSH_USER%@%EC2_HOST% ^

                        "rm -rf ~/invoice-tracker && git clone %GIT_REPO% ~/invoice-tracker"


                        if errorlevel 1 (

                            echo Project clone failed

                            exit /b 1

                        )


                        echo Project cloned successfully

                    '''
                }
            }
        }



        // ==================================================
        // CHECK DOCKER
        // ==================================================

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

                        ssh ^

                        -o StrictHostKeyChecking=no ^

                        -i "%WORKSPACE%\\jenkins-ec2-key.pem" ^

                        %SSH_USER%@%EC2_HOST% ^

                        "docker info"


                        if errorlevel 1 (

                            echo Docker is not working on EC2

                            exit /b 1

                        )


                        echo Docker is working on EC2

                    '''
                }
            }
        }



        // ==================================================
        // BUILD DOCKER IMAGE
        // ==================================================

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

                        ssh ^

                        -o StrictHostKeyChecking=no ^

                        -i "%WORKSPACE%\\jenkins-ec2-key.pem" ^

                        %SSH_USER%@%EC2_HOST% ^

                        "cd ~/invoice-tracker && docker build -t %DOCKER_IMAGE%:%IMAGE_TAG% -t %DOCKER_IMAGE%:latest ."


                        if errorlevel 1 (

                            echo Docker image build failed

                            exit /b 1

                        )


                        echo Docker image built successfully

                    '''
                }
            }
        }



        // ==================================================
        // PUSH DOCKER IMAGE
        // ==================================================

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

                        ssh ^

                        -o StrictHostKeyChecking=no ^

                        -i "%WORKSPACE%\\jenkins-ec2-key.pem" ^

                        %SSH_USER%@%EC2_HOST% ^

                        "docker push %DOCKER_IMAGE%:%IMAGE_TAG% && docker push %DOCKER_IMAGE%:latest"


                        if errorlevel 1 (

                            echo Docker image push failed

                            exit /b 1

                        )


                        echo Docker image pushed successfully

                    '''
                }
            }
        }



        // ==================================================
        // RUN CONTAINER
        // ==================================================

        stage('Run Container') {

            steps {

                echo '========================================'

                echo 'RUN DOCKER CONTAINER'

                echo '========================================'


                withCredentials([

                    sshUserPrivateKey(

                        credentialsId: "${EC2_CREDENTIALS}",

                        keyFileVariable: 'SSH_KEY',

                        usernameVariable: 'SSH_USER'

                    )

                ]) {


                    bat '''

                        ssh ^

                        -o StrictHostKeyChecking=no ^

                        -i "%WORKSPACE%\\jenkins-ec2-key.pem" ^

                        %SSH_USER%@%EC2_HOST% ^

                        "docker rm -f %CONTAINER_NAME% 2>/dev/null || true; docker run -d --name %CONTAINER_NAME% --restart unless-stopped -p %HOST_PORT%:%APP_PORT% %DOCKER_IMAGE%:%IMAGE_TAG%"


                        if errorlevel 1 (

                            echo Container deployment failed

                            exit /b 1

                        )


                        echo Container started successfully

                    '''
                }
            }
        }



        // ==================================================
        // CHECK CONTAINER
        // ==================================================

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

                        ssh ^

                        -o StrictHostKeyChecking=no ^

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



        // ==================================================
        // HEALTH CHECK
        // ==================================================

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


                        timeout /t 10 /nobreak


                        ssh ^

                        -o StrictHostKeyChecking=no ^

                        -i "%WORKSPACE%\\jenkins-ec2-key.pem" ^

                        %SSH_USER%@%EC2_HOST% ^

                        "curl --fail --silent --show-error http://localhost:%HOST_PORT%/"


                        if errorlevel 1 (

                            echo Application health check failed


                            ssh ^

                            -o StrictHostKeyChecking=no ^

                            -i "%WORKSPACE%\\jenkins-ec2-key.pem" ^

                            %SSH_USER%@%EC2_HOST% ^

                            "docker logs %CONTAINER_NAME%"


                            exit /b 1

                        )


                        echo Application health check successful

                    '''
                }
            }
        }

    }



    // ==================================================
    // POST ACTIONS
    // ==================================================

    post {


        success {

            echo '========================================'

            echo 'PIPELINE SUCCESSFUL'

            echo '========================================'


            echo "Docker Image: ${DOCKER_IMAGE}:${IMAGE_TAG}"


            echo "Application URL: http://${EC2_HOST}:${HOST_PORT}"
        }



        failure {

            echo '========================================'

            echo 'PIPELINE FAILED'

            echo '========================================'


            echo 'Check the failed Jenkins stage logs.'
        }



        always {

            echo '========================================'

            echo 'CLEANUP JENKINS WORKSPACE'

            echo '========================================'


            bat '''

                if exist "%WORKSPACE%\\jenkins-ec2-key.pem" (

                    del /F /Q "%WORKSPACE%\\jenkins-ec2-key.pem"

                )

            '''
        }

    }

}