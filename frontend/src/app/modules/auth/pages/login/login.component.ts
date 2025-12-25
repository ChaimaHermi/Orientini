import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { AuthService } from '../../../../services/auth.service';
import { SharedService } from '../../../../services/shared.service';

@Component({
  selector: 'app-login-page',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule
  ],
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss']
})
export class LoginPageComponent {
  form: FormGroup;
  isLoading = false;
  errorMessage = '';
  showPassword = false;

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private sharedService: SharedService,
    private router: Router
  ) {
    this.form = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(6)]],
      rememberMe: [false]
    });
  }

  togglePasswordVisibility(): void {
    this.showPassword = !this.showPassword;
  }

  onSubmit(): void {

  this.form.markAllAsTouched();
  if (this.form.invalid) {
    return;
  }

  const credentials = this.form.value;
  this.isLoading = true;
  this.errorMessage = '';


  // Délai artificiel de 1s pour le spinner
  setTimeout(() => {
    this.authService.login(credentials).subscribe({
      next: (res) => {
        const rememberMe = credentials.rememberMe || false;
        const token = res.access_token;
        if (token) {
          this.sharedService.storeAuthInfo(token, rememberMe);
          this.router.navigate(['/c/default']);
        } else {
          this.errorMessage = 'Erreur d’authentification (token manquant)';
          this.isLoading = false;
        }
      },
      error: (err: any) => {
  console.log('❌ ERREUR LOGIN COMPLETE :', err);
  console.log('➡️ Status HTTP :', err.status);
  console.log('➡️ Body erreur :', err.error);

  this.errorMessage =
    err.error?.detail ||
    err.error?.error ||
    err.message ||
    'Échec de connexion.';

  this.isLoading = false;
}
    });
  }, 1000);
}

onGoogleLogin() {
  this.authService.googleLoginRedirect();
}

  goToRegister(): void {
    this.router.navigate(['/auth/register']);
  }

  goToForgotPassword() {
  this.router.navigate(['/auth/forgot-password']);
}
}
