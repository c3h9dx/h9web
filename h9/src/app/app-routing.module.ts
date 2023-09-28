import {NgModule} from '@angular/core';
import {RouterModule, Routes} from '@angular/router';
import {DashboardComponent} from './dashboard/dashboard.component';
import {DevicesComponent} from './devices/devices.component';
import {RawframeComponent} from './rawframe/rawframe.component';
import {StatsComponent} from './stats/stats.component';
import {SettingsComponent} from './settings/settings.component';
import {CliComponent} from "./cli/cli.component";

const routes: Routes = [
  {path: '', redirectTo: '/dashboard', pathMatch: 'full'},
  {path: 'dashboard', component: DashboardComponent},
  {path: 'devices', component: DevicesComponent},
  {path: 'rawframe', component: RawframeComponent},
  {path: 'stats', component: StatsComponent},
  {path: 'settings', component: CliComponent}
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule {
}
