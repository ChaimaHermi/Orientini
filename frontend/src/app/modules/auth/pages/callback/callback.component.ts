import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { SharedService } from '../../../../services/shared.service';

@Component({
  selector: 'app-callback',
  template: `
    <div class="login-container">
      <div class="login-card">
        <p class="subtitle">Connexion en cours...</p>
      </div>
    </div>
  `
})
export class CallbackComponent implements OnInit {
  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private sharedService: SharedService
  ) {}

ngOnInit(): void {
  const token = this.route.snapshot.queryParamMap.get('token');
  const rememberMe = this.route.snapshot.queryParamMap.get('rememberMe') === 'true';

  console.log("Google callback received:", { token, rememberMe });

  if (token) {
    this.sharedService.storeAuthInfo(token, rememberMe);
    this.router.navigate(['/c/default']);
  } else {
    this.router.navigate(['/auth/login']);
  }
}
}
