import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { AuthService } from '../../../../services/auth.service';
import { SharedService } from '../../../../services/shared.service';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule
  ],
  templateUrl: './register.component.html',
  styleUrls: ['./register.component.scss']
})
export class RegisterPageComponent {
  form: FormGroup;
  isLoading = false;
  errorMessage = '';
  showPassword = false;
  showConfirmPassword = false;

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private sharedService: SharedService,
    private router: Router
  ) {
    this.form = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(6)]],
      confirmPassword: ['', Validators.required],
      rememberMe: [false]
    }, { validator: this.passwordMatchValidator });
  }

  passwordMatchValidator(form: FormGroup) {
    return form.get('password')?.value === form.get('confirmPassword')?.value
      ? null : { mismatch: true };
  }

  togglePasswordVisibility() {
    this.showPassword = !this.showPassword;
  }

  toggleConfirmPasswordVisibility() {
    this.showConfirmPassword = !this.showConfirmPassword;
  }

  onSubmit(): void {

  this.form.markAllAsTouched();
  if (this.form.invalid) {
    return;
  }

const credentials = this.form.value;
this.isLoading = true;
this.errorMessage = '';

setTimeout(() => {
  this.authService.register(credentials).subscribe({
    next: (res) => {
      const token = res.access_token;
      const rememberMe = credentials.rememberMe;

      if (token) {
        this.sharedService.storeAuthInfo(token, rememberMe);
        this.router.navigate(['/c/default']);
      } else {
        this.errorMessage = 'Erreur d’inscription (token manquant)';
        this.isLoading = false;
      }
    },
    error: (err) => {
      this.errorMessage = err.error?.error || 'Échec d’inscription.';
      this.isLoading = false;
    }
  });
}, 1000);

}

goToLogin(): void {
  this.router.navigate(['/auth/login']);
}
}
