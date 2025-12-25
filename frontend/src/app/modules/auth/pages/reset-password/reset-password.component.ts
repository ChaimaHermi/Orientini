import { Component } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { AuthService } from '../../../../services/auth.service';
import { SharedService } from '../../../../services/shared.service';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-reset-password',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule
  ],
  templateUrl: './reset-password.component.html',
  styleUrls: ['./reset-password.component.scss']
})
export class ResetPasswordComponent {
  form: FormGroup;
  token = '';
  isLoading = false;
  successMessage = '';
  errorMessage = '';
  rememberMe = false;
  showPassword = false;

  constructor(
    private route: ActivatedRoute,
    private fb: FormBuilder,
    private authService: AuthService,
    private sharedService: SharedService,
    private router: Router
  ) {
    this.token = this.route.snapshot.queryParamMap.get('token') || '';
    this.rememberMe = this.route.snapshot.queryParamMap.get('rememberMe') === 'true';

    this.form = this.fb.group({
      new_password: ['', [Validators.required, Validators.minLength(6)]]
    });
  }

  onSubmit() {
    if (this.form.invalid) return;

    this.isLoading = true;
    this.successMessage = '';
    this.errorMessage = '';

    this.authService.resetPassword(this.token, this.form.value.new_password).subscribe({
      next: (res) => {
        this.successMessage = res.message;
        this.isLoading = false;

        if (res.access_token) {
          this.sharedService.storeAuthInfo(res.access_token, this.rememberMe);
          this.router.navigate(['/c/default']);
        } else {
          this.router.navigate(['/auth/login']);
        }
      },
      error: (err) => {
        this.errorMessage = err.error?.error || 'Une erreur est survenue.';
        this.isLoading = false;
      }
    });
  }

  togglePasswordVisibility() {
    this.showPassword = !this.showPassword;
  }
  
  goToLogin(): void {
    this.router.navigate(['/auth/login']);
  }
}
