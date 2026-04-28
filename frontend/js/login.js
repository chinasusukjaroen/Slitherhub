/*กดตาเพื่อแสดงรหัสผ่าน*/
        const togglePassword = document.getElementById('toggle-password');
        const passwordInput = document.getElementById('password-input');

        togglePassword.addEventListener('click', function () {
            const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', type);

            
            if (type === 'text') {
                this.style.opacity = '0.5';
            } else {
                this.style.opacity = '1';
            }
        });
