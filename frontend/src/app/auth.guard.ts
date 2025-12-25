import { Injectable } from '@angular/core';
import { CanActivate, Router } from '@angular/router';
import { SharedService } from './services/shared.service';

@Injectable({
  providedIn: 'root'
})
export class AuthGuard implements CanActivate {

  constructor(private sharedService: SharedService, private router: Router) {}

  canActivate(): boolean {
    return this.checkAccess();
  }

    private checkAccess(): boolean {
    const token = this.sharedService.getToken();

    if (token) {
      console.log("correct")
      return true;
    } else {
      console.log("incorrect")
      this.router.navigate(['/auth/login']);
      return false;
    }
  }
}
