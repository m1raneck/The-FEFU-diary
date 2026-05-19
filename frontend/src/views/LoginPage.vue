<template>
  <div class="login-page">
    <div class="background-overlay"></div>
    
    <div class="login-card">
      <div class="avatar"></div>
      
      <h1 class="diary-title">Дневник</h1>
      <div class="divider"></div>
      <h2 class="login-title">Вход</h2>
      
      <form @submit.prevent="handleLogin" class="login-form">
        <div class="input-group">
          <input 
            id="email"
            v-model="form.email"
            type="email"
            placeholder="Почта"
            :class="{ 'error': errors.email }"
            @input="clearError('email')"
          />
          <span v-if="errors.email" class="error-message">{{ errors.email }}</span>
        </div>
        
        <div class="input-group">
          <input 
            id="password"
            v-model="form.password"
            type="password"
            placeholder="Пароль"
            :class="{ 'error': errors.password }"
            @input="clearError('password')"
          />
          <span v-if="errors.password" class="error-message">{{ errors.password }}</span>
        </div>
        
        <button type="submit" class="login-button">Войти</button>
        
        <div class="divider-bottom"></div>
        
        <a href="#" class="forgot-password" @click.prevent="forgotPassword">Забыли пароль?</a>
      </form>
    </div>
  </div>
</template>

<script>
import { login } from "@/services/auth"; // раскомментируй для реального бэкенда

export default {
  name: 'LoginPage',
  data() {
    return {
      form: {
        email: '',
        password: ''
      },
      errors: {
        email: '',
        password: ''
      }
    }
  },
  methods: {
    validateEmail(email) {
      const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      return re.test(email)
    },
    
    validateForm() {
      let isValid = true
      
      if (!this.form.email) {
        this.errors.email = 'Пожалуйста, введите почту'
        isValid = false
      } else if (!this.validateEmail(this.form.email)) {
        this.errors.email = 'Введите корректный email (например, name@domain.com)'
        isValid = false
      }
      
      if (!this.form.password) {
        this.errors.password = 'Пожалуйста, введите пароль'
        isValid = false
      } else if (this.form.password.length < 4) {
        this.errors.password = 'Пароль должен содержать минимум 4 символа'
        isValid = false
      }
      
      return isValid
    },
    
    clearError(field) {
      this.errors[field] = ''
    },
    
    async handleLogin() {
      if (!this.validateForm()) return
  try {
    await login(this.form.email, this.form.password)
    this.$router.push('/schedule')
  } catch (e) {
    this.errors.password = e.message || 'Ошибка входа'
  }
    },
    
    forgotPassword() {
        this.$router.push('/forgot-password')
    }
  }
}
</script>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.login-page {
  min-height: 100vh;
  width: 100%;
  background: linear-gradient(63deg, rgba(15, 80, 110, 0.2) 17%, rgba(153, 191, 230, 0.2) 65%),
              linear-gradient(0deg, #465C73 0%, #465C73 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  position: relative;
}

.login-card {
  position: relative;
  width: 100%;
  max-width: 491px;
  background: linear-gradient(145deg, rgba(193, 200, 206, 0.9) 31%, 
              rgba(183, 192, 200, 0.9) 47%, 
              rgba(139, 153, 171, 0.9) 100%);
  border: 2px solid rgba(255, 255, 255, 0.78);
  border-radius: 30px;
  box-shadow: 0px 4px 4px rgba(0, 0, 0, 0.25);
  padding: 2rem 2rem 3rem;
}

.avatar {
  width: 52px;
  height: 52px;
  background-color: #667593;
  border-radius: 50%;
  box-shadow: inset 0px 4px 4px rgba(0, 0, 0, 0.25);
  position: absolute;
  margin-top: 1.2rem;
  left: 6rem;
}

.diary-title {
  font-family: system-ui, 'Inter', -apple-system, sans-serif;
  font-weight: 500;
  font-size: clamp(24px, 5vw, 32px);
  color: #38445E;
  text-align: center;
  margin-top: 1.5rem;
  margin-bottom: 1rem;
}

.divider {
  height: 1px;
  background: linear-gradient(to right, transparent, #899bbf, transparent);
  width: 100%;
  margin-bottom: 1rem;
  margin-top: 0.5rem;
  opacity: 0.5;
}

.login-title {
  font-family: system-ui, 'Inter', -apple-system, sans-serif;
  font-weight: 350;
  font-size: clamp(24px, 5vw, 32px);
  color: #38445E;
  text-align: center;
  margin-top: 0.5rem;
  margin-bottom: 2rem;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.input-group input {
  width: 100%;
  padding: 1rem;
  font-size: 16px;
  font-family: system-ui, 'Inter', -apple-system, sans-serif;
  background-color: #e6e6e6;
  border: 2px solid transparent;
  border-radius: 10px;
  transition: all 0.3s ease;
  outline: none;
}

.input-group input:focus {
  border-color: #667593;
  background-color: #fff;
  box-shadow: 0 0 0 3px rgba(102, 117, 147, 0.2);
}

.input-group input.error {
  border-color: #dc3545;
  background-color: #fff8f8;
}

.error-message {
  color: #dc3545;
  font-family: system-ui, 'Inter', -apple-system, sans-serif;
  font-size: 14px;
  margin-top: -0.25rem;
}

.login-button {
  background-color: #667593;
  color: #ffffff;
  font-family: system-ui, 'Inter', -apple-system, sans-serif;
  font-weight: 800;
  font-size: 20px;
  height: 80px;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 1rem;
}

.login-button:hover {
  background-color: #4a5a73;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.login-button:active {
  transform: translateY(0);
}

.divider-bottom {
  height: 1px;
  background: linear-gradient(to right, transparent, #505e7b, transparent);
  width: 100%;
  margin: 0.5rem 0;
  opacity: 0.5;
}

.forgot-password {
  font-family: system-ui, 'Inter', -apple-system, sans-serif;
  font-weight: 400;
  font-size: 20px;
  color: #000000;
  text-align: center;
  text-decoration: none;
  transition: all 0.3s ease;
  display: block;
}

.forgot-password:hover {
  color: #dc3545;
  text-decoration: underline;
}


@media (max-width: 768px) {
  .login-card {
    padding: 1.5rem;
    max-width: 90%;
  }
  
  .login-button {
    height: 65px;
    font-size: 18px;
    width: 500px;
    margin-left: 3.5rem;
    height:70px;
  }
  
  .forgot-password {
    font-size: 18px;
    margin-top: -0.5rem;

  }
  
  .input-group input {
    padding: 0.875rem;
    width: 500px;
    margin-left: 3.5rem;
    height:60px;
  }
  
  .avatar {
    width: 45px;
    height: 44px;
    top: 32px;
    left: 50px;
  }
}

@media (max-width: 560px) {
  .login-card {
    padding: 1.25rem;
  }
  
  .login-button {
    height: 55px;
    font-size: 16px;
  }
  
  .forgot-password {
    font-size: 14px;
  }
  
  .input-group input {
    padding: 0.75rem;
  }
  
  .avatar {
    width: 38px;
    height: 38px;
    top: 28px;
    left: 35px;
  }
}

@media (max-width: 400px) {
  .avatar {
    width: 32px;
    height: 32px;
    top: 24px;
    left: 25px;
  }
}
</style>