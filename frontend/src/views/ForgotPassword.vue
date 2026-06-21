<template>
  <div class="screen" :class="{ 'is-mobile': isMobile }">
    <div class="login-card">
      <div class="card-content">
        <div class="title-section">
          <div class="icon-wrapper">
            <img src="@/assets/icon.png" alt="Icon" class="icon" />
          </div>
          <div class="logo">
            <div class="logo-main">UniDiary</div>
            <div class="logo-sub">ЭЛЕКТРОННЫЙ ДНЕВНИК</div>
          </div>
          <div class="line"></div>
        </div>

        <form @submit.prevent="handleReset" class="form-section">
          <div class="input-field">
            <label class="field-label">Email</label>
            <input
              v-model="email"
              type="email"
              placeholder="example@mail.com"
              :class="{ 'error': error }"
              @input="error = ''"
            />
            <span v-if="error" class="error-message">{{ error }}</span>
          </div>
          <div class="info-text">На указанную почту<br> придёт ссылка для восстановления пароля</div>
          <button type="submit" class="reset-button" :disabled="loading">Отправить ссылку</button>
          <a href="#" class="back-link" @click.prevent="goBack">← Вернуться ко входу</a>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { requestPasswordReset } from "@/services/auth";

export default {
  name: 'ForgotPassword',
  data() {
    return {
      email: '',
      error: '',
      loading: false,
      isMobile: false
    }
  },
  mounted() {
    this.checkIfMobile();
    window.addEventListener('resize', this.checkIfMobile);
  },
  beforeDestroy() {
    window.removeEventListener('resize', this.checkIfMobile);
  },
  methods: {
    checkIfMobile() {
      this.isMobile = window.innerWidth < 768;
    },
    validateEmail(email) {
      const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      return re.test(email);
    },
    async handleReset() {
      if (!this.email) {
        this.error = 'Пожалуйста, введите почту';
        return;
      }
      if (!this.validateEmail(this.email)) {
        this.error = 'Введите корректный email';
        return;
      }

      this.loading = true;
      this.error = '';
      try {
        await requestPasswordReset(this.email);
        alert(`Ссылка для восстановления пароля отправлена на ${this.email}`);
        setTimeout(() => {
          this.$router.push('/');
        }, 2000);
      } catch (err) {
        this.error = err.message || 'Ошибка отправки. Попробуйте позже.';
      } finally {
        this.loading = false;
      }
    },
    goBack() {
      this.$router.push('/');
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

.screen {
  min-height: 100vh;
  width: 100%;
  background-image: url('@/assets/image.png');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  background-color: #919ba4;
  background-blend-mode: overlay;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.screen.is-mobile {
  background-image: url('@/assets/main2.PNG');
  background-color: #49709ac2;
  background-blend-mode: overlay;
  background-position: left center;
  position: relative;
}
.screen.is-mobile::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, rgba(255,255,255,0.35) 0%, rgba(255,255,255,0.1) 100%);
  pointer-events: none;
  z-index: 0;
}
.screen.is-mobile > * {
  position: relative;
  z-index: 1;
}

.login-card {
  width: 100%;
  max-width: 560px;
  backdrop-filter: blur(6px) brightness(110%);
  background: linear-gradient(
    145deg,
    rgba(255, 255, 255, 0.55) 22%,
    rgba(188, 207, 226, 0.35) 79%,
    rgba(149, 169, 195, 0.55) 100%
  );
  border: 1px solid rgba(255, 255, 255, 0.85);
  border-radius: 38px;
  box-shadow: 0px 12px 28px rgba(0, 0, 0, 0.25);
  padding: 3rem 3rem 3.2rem;
}

.card-content {
  display: flex;
  flex-direction: column;
  gap: 2.5rem;
}

.title-section {
  text-align: center;
  margin-bottom: 0.25rem;
}

.icon-wrapper {
  text-align: center;
  margin-bottom: 12px;
}
.icon {
  width: 80px;
  height: auto;
  object-fit: contain;
}

.logo {
  margin-bottom: 16px;
}
.logo-main {
  color: #2c3e4f;
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
  font-size: 46px;
  font-weight: 800;
  letter-spacing: -0.5px;
}
.logo-sub {
  color: #4a5a7a;
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
  font-size: 13px;
  font-weight: 500;
  letter-spacing: 1.5px;
  margin-top: 6px;
  text-transform: uppercase;
}

.line {
  height: 2px;
  background: #566697;
  width: 60%;
  margin: 0 auto;
  opacity: 0.4;
}

.form-section {
  display: flex;
  flex-direction: column;
  gap: 5rem;
}

.input-field {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.field-label {
  color: #ffffff;
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
  font-size: 16px;
  font-weight: 600;
  margin-left: 0.5rem;
  text-shadow: 0 1px 2px rgba(0,0,0,0.2);
}

.input-field input {
  background-color: rgba(255, 255, 255, 0.35);
  border: 2px solid rgba(255, 255, 255, 0.9);
  border-radius: 44px;
  padding: 16px 24px;
  font-size: 16px;
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
  color: #395d97;
  outline: none;
  transition: all 0.25s ease;
  width: 100%;
}

.input-field input::placeholder {
  color: rgba(255, 255, 255, 0.8);
  font-weight: 500;
}

.input-field input:focus {
  border-color: #6f8bc0;
  background-color: rgba(255, 255, 255, 0.55);
}

.input-field input.error {
  border-color: #806cc4;
  background-color: rgba(163, 107, 203, 0.2);
  box-shadow: 0 0 0 3px rgba(242, 194, 214, 0.1);
}

.error-message {
  color: #653897;
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
  font-size: 12px;
  margin-left: 0.75rem;
  font-weight: 500;
}

.info-text {
  color: #ffffff;
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
  font-size: 14px;
  font-weight: 400;
  text-align: center;
  margin: 0;
  opacity: 0.5;
  letter-spacing: 0.2px;
  margin-bottom: -3.5rem; 
}

.reset-button {
  background-color: #283347;
  border-radius: 44px;
  box-shadow: 0px 6px 12px rgba(0, 0, 0, 0.3);
  border: none;
  color: #f0f5fc;
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
  font-size: 22px;
  font-weight: 700;
  padding: 24px 20px;
  cursor: pointer;
  transition: all 0.25s ease;
  width: 100%;
  margin-top: 0;
}

.reset-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.reset-button:hover:not(:disabled) {
  background-color: #1c253b;
  transform: translateY(-3px);
  box-shadow: 0 10px 18px rgba(0, 0, 0, 0.35);
}

.back-link {
  color: #1a1f2c;
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
  font-size: 18px;
  font-weight: 600;
  text-align: center;
  text-decoration: none;
  transition: color 0.2s;
  margin-top: 0.5rem;
  letter-spacing: 0.3px;
}

.back-link:hover {
  color: #275b97;
}

@media (max-width: 640px) {
  .screen {
    padding: 1rem;
  }
  .login-card {
    max-width: 92%;
    padding: 2rem 1.5rem 2.5rem;
  }
  .icon {
    width: 50px;
  }
  .logo-main {
    font-size: 34px;
  }
  .logo-sub {
    font-size: 10px;
  }
  .reset-button {
    font-size: 20px;
    padding: 14px;
  }
  .back-link {
    font-size: 16px;
  }
  .info-text {
    font-size: 12px;
    margin-bottom: -1rem;
  }
  .card-content {
    gap: 2rem;
  }
  .form-section {
    gap: 2rem;
  }
}
</style>