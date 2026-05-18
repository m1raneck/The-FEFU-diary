<template>
  <div class="login-page">
    <div class="background-overlay"></div>
    
    <div class="login-card">
      <div class="avatar"></div>
      
      <h1 class="diary-title">Дневник</h1>
      <div class="divider"></div>
      <h2 class="login-title">Восстановление пароля</h2>
      
      <form @submit.prevent="handleReset" class="login-form">
        <div class="input-group">
          <input 
            id="email"
            v-model="email"
            type="email"
            placeholder="Введите почту"
            :class="{ 'error': error }"
            @input="error = ''"
          />
          <span v-if="error" class="error-message">{{ error }}</span>
        </div>
        
        <button type="submit" class="login-button">Отправить ссылку</button>
        
        <div class="divider-bottom"></div>
        
        <a href="#" class="back-link" @click.prevent="goBack">← Вернуться ко входу</a>
      </form>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ForgotPassword',
  data() {
    return {
      email: '',
      error: ''
    }
  },
  methods: {
    validateEmail(email) {
      const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      return re.test(email)
    },
    
    handleReset() {
      if (!this.email) {
        this.error = 'Пожалуйста, введите почту'
        return
      }
      
      if (!this.validateEmail(this.email)) {
        this.error = 'Введите корректный email'
        return
      }
      
      // здесь должен быть запрос на сервер
      console.log('Сброс пароля для:', this.email)
      alert(`Ссылка для восстановления пароля отправлена на ${this.email}`)
      
      // через 2 секунды возвращается на страницу входа
      setTimeout(() => {
        this.$router.push('/')
      }, 2000)
    },
    
    goBack() {
      this.$router.push('/')
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
  font-weight: 400;
  font-size: clamp(16px, 5vw, 24px);
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
  margin-top: 2rem;
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
  font-weight: 750;
  font-size: 20px;
  height: 70px;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 5rem;
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
  margin-top: 1rem;
  margin-bottom: 0.5rem;
  opacity: 0.5;
}

.back-link {
  font-family: system-ui, 'Inter', -apple-system, sans-serif;
  font-weight: 400;
  font-size: 20px;
  color: #000000;
  text-align: center;
  text-decoration: none;
  transition: all 0.3s ease;
  margin-top: 0.1rem;
  display: block;
}

.back-link:hover {
  color: #667593;
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
    height: 70px;
  }
  
  .back-link {
    font-size: 18px;
  }
  
  .input-group input {
    padding: 0.875rem;
    width: 500px;
    margin-left: 3.5rem;
    height: 65px;
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
  
  .back-link {
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