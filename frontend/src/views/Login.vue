<template>
	<div class="login-container">
		<!-- Logo Container -->
		<div class="logo-container">
			<LogoComponent class="logo-animation" />
		</div>

		<!-- Login Form -->
		<div class="form-container">
			<h1 class="text-xl font-bold text-gray-900 mb-4 text-center">{{ $t('signin') }}</h1>

			<form @submit.prevent="login" class="space-y-4">
				<div class="input-group">
					<FloatLabel>
						<InputText v-model="email" id="email" class="w-full" :placeholder="$t('username')" />
						<label for="email">{{ $t('username') }}</label>
					</FloatLabel>
				</div>

				<div class="input-group">
					<FloatLabel>
						<InputText v-model="password" id="password" type="password" class="w-full"
							:placeholder="$t('password')" />
						<label for="password">{{ $t('password') }}</label>
					</FloatLabel>
				</div>

				<div v-if="errorMessage" class="error-message">
					{{ errorMessage }}
				</div>

				<Button type="submit" :label="isLoggingIn ? $t('signingIn') : $t('signin')" icon="pi pi-sign-in"
					class="w-full p-button-md" :loading="isLoggingIn" />
			</form>
		</div>

		<!-- Footer -->
		<div class="footer">
			<p class="text-sm text-gray-500">© {{ new Date().getFullYear() }} Invoice Form</p>
		</div>

		<!-- Toast for notifications -->
		<Toast position="bottom-right" />
	</div>
</template>

<script>
import axios from 'axios';
import { useToast } from 'primevue/usetoast';
import LogoComponent from '../components/LogoComponent.vue';

export default {
	components: {
		LogoComponent
	},
	data() {
		return {
			email: null,
			password: null,
			errorMessage: null,
			isLoggingIn: false,
		};
	},
	inject: ["$auth", "$permissions"],
	setup() {
		const toast = useToast();
		return { toast };
	},
	mounted() {
		// Responsive viewport height handling
		this.adjustHeight();
		window.addEventListener('resize', this.adjustHeight);

		if (this.$route?.query?.route) {
			this.redirect_route = this.$route.query.route;
			this.$router.replace({ query: null });
		}
	},
	beforeUnmount() {
		window.removeEventListener('resize', this.adjustHeight);
	},
	methods: {
		adjustHeight() {
			const vh = window.innerHeight * 0.01;
			document.documentElement.style.setProperty('--vh', `${vh}px`);
		},
		async login() {
  this.errorMessage = null;
  this.isLoggingIn = true;

  if (!this.email || !this.password) {
    this.errorMessage = this.$t('enterBothCredentials');
    this.isLoggingIn = false;
    return;
  }

  try {
    const result = await this.$auth.login(this.email, this.password);

    if (result) {
      // Load user permissions after login
      await this.$permissions.loadPermissions(this.email);

      if (!this.$permissions.hasPermission("can_login")) {
        this.errorMessage = this.$t('noLoginPermission');
        this.toast.add({
          severity: 'error',
          summary: this.$t('accessDenied'),
          detail: this.$t('noLoginPermission'),
          life: 3000
        });

        // 🚨 Force logout + reload to reset session state
        await this.$auth.logout();
        setTimeout(() => {
          window.location.href = "/invoice_form/login"; // or just: location.reload();
        }, 500);

        return;
      }

      // ✅ Permission OK, continue
      this.toast.add({
        severity: 'success',
        summary: this.$t('loginSuccessful'),
        detail: this.$t('welcomeBack'),
        life: 3000
      });

      setTimeout(() => {
        this.$router.push({ name: "Home" });
      }, 300);
    } else {
      this.errorMessage = this.$t('invalidCredentials');
    }
  } catch (error) {
    console.error("Login error:", error);

    if (error.exc_type === "AuthenticationError") {
      this.errorMessage = this.$t('invalidCredentials');
    } else {
      this.errorMessage = this.$t('loginError');
      this.toast.add({
        severity: 'error',
        summary: this.$t('loginError'),
        detail: this.$t('tryAgainLater'),
        life: 3000
      });
    }
  } finally {
    this.isLoggingIn = false;
  }
}

	}
};
</script>

<style scoped>
.login-container {
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: space-between;
	padding: 2rem 1rem;
	/* Use CSS custom property for true viewport height */
	height: calc(var(--vh, 1vh) * 100);
	max-height: 100vh;
	box-sizing: border-box;
	background-color: #f9fafb;
}

.logo-container {
	width: 100%;
	max-width: min(60vw, 180px);
	display: flex;
	justify-content: center;
	margin-bottom: 2rem;
	margin-top: 2rem;
	flex-shrink: 1;
}

.logo-animation {
	width: 100%;
	height: auto;
	animation: float 6s infinite ease-in-out;
	max-height: 25vh;
}

.form-container {
	width: 100%;
	max-width: 320px;
	padding: 1.5rem;
	background: white;
	border-radius: 8px;
	box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05), 0 1px 3px rgba(0, 0, 0, 0.1);
}

.input-group {
	margin-bottom: 1.5rem;
}

.error-message {
	color: #ef4444;
	font-size: 0.875rem;
	margin-bottom: 1rem;
}

.footer {
	margin-top: 2rem;
	text-align: center;
	padding: 1rem 0;
}

/* Button styling */
:deep(.p-button-md) {
	height: 3rem;
	font-size: 1rem;
}

@keyframes float {
	0% {
		transform: translateY(0px);
	}

	50% {
		transform: translateY(-10px);
	}

	100% {
		transform: translateY(0px);
	}
}

/* Media query for larger screens */
@media (min-height: 700px) {
	.form-container {
		padding: 2rem;
		max-width: 360px;
	}
}

/* Media query for very small screens */
@media (max-height: 500px) {
	.login-container {
		padding: 1rem;
	}

	.logo-container {
		max-width: 120px;
		margin-bottom: 1rem;
		margin-top: 0.5rem;
	}

	.form-container {
		padding: 1rem;
	}

	.input-group {
		margin-bottom: 1rem;
	}

	:deep(.p-button-md) {
		height: 2.5rem;
		font-size: 0.9rem;
	}
}
</style>