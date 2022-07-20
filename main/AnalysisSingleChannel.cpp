#include "CfgManager/interface/CfgManager.h"
#include "CfgManager/interface/CfgManagerT.h"
 
#include "interface/SetTDRStyle.h"  

#include "TROOT.h"
#include "TStyle.h"
#include "TFile.h"
#include "TF1.h"
#include "TH1.h"
#include "TH2.h"
#include "TRandom.h"
#include "TProfile.h"
#include "TCanvas.h"
#include "TGraphErrors.h"
#include "TLine.h"
#include "TLegend.h"
#include "TChain.h"
#include "TVirtualFitter.h"
#include "TLatex.h"
#include "TMath.h"
#include "TVector3.h"
#include "TVector2.h"
#include "TLorentzVector.h"
#include "TMath.h"
#include "TApplication.h"

#include <iostream>
#include <iomanip>
#include <string>
#include <sstream>
#include <ctime>
#include <map>
#include <algorithm>
#include <cmath>


using namespace std;



int main(int argc, char** argv){
  
  //--- parse the config file
  //  CfgManager opts;
  //opts.ParseConfigFile(argv[1]);

  //int run  = opts.GetOpt<int>("Inputs.run");
  
  //std::string plotDir = opts.GetOpt<std::string>("Output.plotDir");
  //system(Form("mkdir -p %s",plotDir.c_str()));

  
  int run = 5352;

  std::string plotDir(Form("/var/www/html/TOFHIR2B/MTDTB_CERN_June22/analysisSingleChannel/%04d/",run ));
  system(Form("mkdir -p %s",plotDir.c_str()));  

  int chRef = 65;
  std::cout<< "Reference channel :  " <<  chRef <<std::endl;

  int maxActiveChannels0 = 2;
  int maxActiveChannels1 = 2;

  // --- reading tree
  TChain* tree = new TChain("data","data");
  tree->Add(Form("/data1/cmsdaq/tofhir2/h8/reco/%d/*_e.root", run));

  //--- define branches
  float step1, step2;
  int channelIdx[128];
  std::vector<float> *tot = 0;
  std::vector<float> *energy = 0;
  std::vector<long long> *time = 0;
  std::vector<unsigned short>* t1fine = 0;
  
  tree -> SetBranchStatus("*",0);
  tree -> SetBranchStatus("step1",  1); tree -> SetBranchAddress("step1",  &step1);
  tree -> SetBranchStatus("step2",  1); tree -> SetBranchAddress("step2",  &step2);
  tree -> SetBranchStatus("channelIdx",  1); tree -> SetBranchAddress("channelIdx",  channelIdx);
  tree -> SetBranchStatus("tot",    1); tree -> SetBranchAddress("tot",       &tot);
  tree -> SetBranchStatus("energy", 1); tree -> SetBranchAddress("energy", &energy);
  tree -> SetBranchStatus("time",   1); tree -> SetBranchAddress("time",     &time);
  tree -> SetBranchStatus("t1fine",   1); tree -> SetBranchAddress("t1fine",     &t1fine);

  int nEntries = tree->GetEntries();
  cout << "Number of entries = " << nEntries << endl;
  //int maxEntries = 12000000;
  int maxEntries = nEntries;
  


  // -- book histograms 
  TH1F *h_nActiveChannels0 = new TH1F("h_nActiveChannels0","h_nActiveChannels0",32,-0.5,31.5);
  TH1F *h_nActiveChannels1 = new TH1F("h_nActiveChannels1","h_nActiveChannels1",32,-0.5,31.5);

  TH1F *h_energy_chRef = new TH1F("h_energy_chRef","h_energy_chRef",1024,0,1024);

  map<int,TH1F*>   h_energy;
  map<int,TH1F*>   h_totRatio;
  map<int,TH1F*>   h_deltaT;
  map<int,TH1F*>   h_deltaT_totRatioCorr;
  map<int,TH1F*>   h_deltaT_totRatioCorr_phaseCorr;
  map<int,TProfile*>  p_deltaT_vs_totRatio;
  map<int,TProfile*>  p_deltaT_totRatioCorr_vs_t1fine;
  map<int,TH2F*>  h2_deltaT_totRatioCorr_vs_t1fine;
  map<int,TProfile*>  p_deltaT_totRatioCorr_vs_t1fineRef;
  map<int,TH2F*>  h2_deltaT_totRatioCorr_vs_t1fineRef;

  for (int ch = 0; ch < 32; ch++){
    h_energy[ch] = new TH1F(Form("h_energy_ch%02d",ch) , Form("h_energy_ch%02d",ch), 1024, 0, 1024);
    h_totRatio[ch] = new TH1F(Form("h_totRatio_ch%02d",ch) , Form("h_totRatio_ch%02d",ch), 100, 0, 3);
    h_deltaT[ch] = new TH1F(Form("h_deltaT_ch%02d",ch) , Form("h_deltaT_ch%02d",ch), 2000, -12000, 12000);
    h_deltaT_totRatioCorr[ch] = new TH1F(Form("h_deltaT_totRatioCorr_ch%02d",ch) , Form("h_deltaT_totRatioCorr_ch%02d",ch), 2000, -12000, 12000);
    h_deltaT_totRatioCorr_phaseCorr[ch] = new TH1F(Form("h_deltaT_totRatioCorr_phaseCorr_ch%02d",ch) , Form("h_deltaT_totRatioCorr_phaseCorr_ch%02d",ch), 2000, -12000, 12000);
    p_deltaT_vs_totRatio[ch] = new TProfile(Form("p_deltaT_vs_totRatio_ch%02d",ch) , Form("p_deltaT_vs_totRatio_ch%02d",ch), 300, 0, 3);
    p_deltaT_totRatioCorr_vs_t1fine[ch] = new TProfile(Form("p_deltaT_totRatioCorr_vs_t1fine_ch%02d",ch) , Form("p_deltaT_totRatioCorr_vs_t1fine_ch%02d",ch), 50, 0, 1000);
    h2_deltaT_totRatioCorr_vs_t1fine[ch] = new TH2F(Form("h2_deltaT_totRatioCorr_vs_t1fine_ch%02d",ch) , Form("h2_deltaT_totRatioCorr_vs_t1fine_ch%02d",ch), 50, 0, 1000, 2000, -12000, 12000);
    p_deltaT_totRatioCorr_vs_t1fineRef[ch] = new TProfile(Form("p_deltaT_totRatioCorr_vs_t1fineRef_ch%02d",ch) , Form("p_deltaT_totRatioCorr_vs_t1fineRef_ch%02d",ch), 50, 0, 1000);
    h2_deltaT_totRatioCorr_vs_t1fineRef[ch] = new TH2F(Form("h2_deltaT_totRatioCorr_vs_t1fineRef_ch%02d",ch) , Form("h2_deltaT_totRatioCorr_vs_t1fineRef_ch%02d",ch), 50, 0, 1000, 2000, -12000, 12000);
  }

  TH1F *h_deltaT_LR       = new TH1F("h_deltaT_LR","h_deltaT_LR",  2000, -12000, 12000); 
  TH1F *h_deltaT_LR_chRef = new TH1F("h_deltaT_LR_chRef","h_deltaT_LR_chRef",  2000, -12000, 12000); 


  map <int, map<int, bool> > acceptEvent;
  map <int, map<int, bool> > acceptEvent_chRef;

  map<int, int>  nActiveChannels0;
  map<int, int>  nActiveChannels1;

  // -- first loop over events
  cout << "First loop over events to find the mip peak" <<endl;
  for (int entry = 0; entry < maxEntries; entry++){
    
    tree->GetEntry(entry);

    if( entry%1000 == 0 ) std::cout << ">>> Reading entry " << entry << " / " << nEntries << "\r" << std::flush;

    // -- count active channels in the two modules
    nActiveChannels0[entry] = 0;
    for (int ch = 0; ch < 32; ch++) {
      if ( channelIdx[ch] < 0 ) continue;                                                                                                                                       
      if ( (*tot)[channelIdx[ch]]/1000 < -10. || (*tot)[channelIdx[ch]]/1000 > 50. ) continue;                                                                                  
      if ((*energy)[channelIdx[ch]] > 0)                                                                                                                                        
	nActiveChannels0[entry]+=1;                                                                                                                                              
    }    

    nActiveChannels1[entry] = 0;
    for (int ch = 64; ch < 96 ; ch++) {
      if ( channelIdx[ch] < 0 ) continue;                                                                                                                                       
      if ( (*tot)[channelIdx[ch]]/1000 < -10. || (*tot)[channelIdx[ch]]/1000 > 50. ) continue;                                                                                  
      if ((*energy)[channelIdx[ch]] > 0)                                                                                                                                        
	nActiveChannels1[entry]+=1;                                                                                                                                              
    }    


    h_nActiveChannels0 ->Fill(nActiveChannels0[entry]);
    h_nActiveChannels1 ->Fill(nActiveChannels1[entry]);

    if (nActiveChannels0[entry] >  maxActiveChannels0) continue;
    if (nActiveChannels1[entry] >  maxActiveChannels1) continue;


    //-- ref channel
    if ( channelIdx[chRef] < 0 ) continue;
    if ( (*tot)[channelIdx[chRef]]/1000 < -10. || (*tot)[channelIdx[chRef]]/1000 > 50. ) continue;      

    h_energy_chRef -> Fill( (*energy)[channelIdx[chRef]] ); 
    
    for (int ch = 0; ch < 32; ch++) {
	
      if ( channelIdx[ch] < 0 ) continue;
      if ( (*tot)[channelIdx[ch]]/1000 < -10. || (*tot)[channelIdx[ch]]/1000 > 50. ) continue;
      
      if ((*energy)[channelIdx[ch]]) 
      h_energy[ch] -> Fill( (*energy)[channelIdx[ch]] );	
    }

  }// -- end first loop over entries


  // -- find min energy
  TF1 *fitLandau_chRef = new TF1("fitLandau_chRef","landau", 0, 1000);
  h_energy_chRef->GetXaxis()->SetRangeUser(300,800);
  int maxbin = h_energy_chRef->GetMaximumBin();
  float peak = h_energy_chRef->GetBinCenter(maxbin);
  fitLandau_chRef->SetRange(peak*0.8, peak*1.2);
  fitLandau_chRef->SetParameter(1,peak);
  fitLandau_chRef->SetParameter(2,0.1*peak);
  h_energy_chRef->Fit("fitLandau_chRef","QR");
  float energyMin_chRef = fitLandau_chRef->GetParameter(1)*0.8;
  h_energy_chRef->GetXaxis()->SetRangeUser(0,1000);

  map<int, float> energyMin;
  map<int, TF1*> fitLandau;
  
  for (int ch = 0; ch < 32 ; ch++){
    fitLandau[ch] = new TF1(Form("fitLandau_ch%02d",ch),"landau", 0, 1000);    
    h_energy[ch]->GetXaxis()->SetRangeUser(300,800);
    if (ch == 11) h_energy[ch]->GetXaxis()->SetRangeUser(50,800);
    int maxbin = h_energy[ch]->GetMaximumBin();
    float peak = h_energy[ch]->GetBinCenter(maxbin);
    fitLandau[ch]->SetRange(peak*0.85, peak*1.2);
    fitLandau[ch]->SetParameter(1,peak);
    fitLandau[ch]->SetParameter(2,0.1*peak);
    h_energy[ch]->Fit(fitLandau[ch],"QR");
    energyMin_chRef = fitLandau[ch]->GetParameter(1)*0.85;
    h_energy[ch]->GetXaxis()->SetRangeUser(0,1000);
  }


  // -- second loop over events to get amp walk corrections
  cout << "Second loop over events to get amp walk corrections" <<endl;
  for (int entry = 0; entry < maxEntries; entry++){
    
    if( entry%1000 == 0 ) std::cout << ">>> Reading entry " << entry << " / " << nEntries << "\r" << std::flush;
    tree->GetEntry(entry);

    acceptEvent_chRef[entry][chRef] = false;
   
    // -- remove showering events
    if (nActiveChannels0[entry] > maxActiveChannels0) continue;
    if (nActiveChannels1[entry] > maxActiveChannels1) continue;

    //-- ref channel
    if ( channelIdx[chRef] < 0 ) continue;
    if ( (*tot)[channelIdx[chRef]]/1000 < -10. || (*tot)[channelIdx[chRef]]/1000 > 50. ) continue;
    if ( (*energy)[channelIdx[chRef]] < energyMin_chRef || (*energy)[channelIdx[chRef]] > 900) continue;

    acceptEvent_chRef[entry][chRef] = true;

    // -- single channels
    for (int ch = 0; ch < 32; ch++) {

      acceptEvent[entry][ch] = false;
       
      if ( channelIdx[ch] < 0 ) continue;
      if ( (*tot)[channelIdx[ch]]/1000 < -10. || (*tot)[channelIdx[ch]]/1000 > 50. ) continue;
      if ( (*energy)[channelIdx[ch]] < energyMin[ch] || (*energy)[channelIdx[ch]] > 900 ) continue;
      //if ( (*tot)[channelIdx[ch]]/(*tot)[channelIdx[chRef]] >  (fitFun_totRatio[ch]->GetParameter(1)+3*fitFun_totRatio[ch]->GetParameter(2)) ) continue;
      //if ( (*tot)[channelIdx[ch]]/(*tot)[channelIdx[chRef]] <  (fitFun_totRatio[ch]->GetParameter(1)-3*fitFun_totRatio[ch]->GetParameter(2)) ) continue;
      
      acceptEvent[entry][ch] = true;
      
      float deltaT = (*time)[channelIdx[ch]] - (*time)[channelIdx[chRef]];
      
      if ( fabs(deltaT)>10000) continue;

      h_deltaT[ch]   -> Fill( deltaT );	
      h_totRatio[ch] -> Fill( (*tot)[channelIdx[ch]]/(*tot)[channelIdx[chRef]] );	
      p_deltaT_vs_totRatio[ch] -> Fill( (*tot)[channelIdx[ch]]/(*tot)[channelIdx[chRef]] , deltaT );	
    
    }
    
    // fill deltaT L-R for two bars
    int ch1 = 4;
    int ch2 = 27;
    if ( acceptEvent[entry][ch1]  && acceptEvent[entry][ch2]  && acceptEvent_chRef[entry][chRef])    {
      h_deltaT_LR ->Fill(  (*time)[channelIdx[ch1]] - (*time)[channelIdx[ch2]] );
      h_deltaT_LR_chRef ->Fill(  (*time)[channelIdx[chRef]] - (*time)[channelIdx[94]] );
    }

  }// -- end second loop over entries
  
  
  // ---  amp walk corr
  map<int,TF1*> fitFun_totRatio;
  map<int,TF1*> fitFun_totRatioCorr;
  for (int ch = 0; ch < 32; ch++) {   

    fitFun_totRatio[ch] = new TF1(Form("fitFun_totRatio_ch%02d",ch), "gaus", 0,10);  
    h_totRatio[ch] -> Fit(fitFun_totRatio[ch]);

    fitFun_totRatioCorr[ch] = new TF1(Form("fitFun_totRatioCorr_ch%02d",ch), "pol3", 0,10);
    fitFun_totRatioCorr[ch]->SetRange( fitFun_totRatio[ch]->GetParameter(1) - 3*fitFun_totRatio[ch]->GetParameter(2), fitFun_totRatio[ch]->GetParameter(1) + 3*fitFun_totRatio[ch]->GetParameter(2) );
    //fitFun_totRatioCorr[ch]->SetRange( p_deltaT_vs_totRatio[ch] -> GetMean() - 3*p_deltaT_vs_totRatio[ch]-> GetRMS(),p_deltaT_vs_totRatio[ch] -> GetMean() + 3*p_deltaT_vs_totRatio[ch]-> GetRMS()  );
    p_deltaT_vs_totRatio[ch] -> Fit(fitFun_totRatioCorr[ch],"QRS");
  }
  
  // -- third loop over events to apply amp walk corrections
  cout << "Third loop over events to apply amp walk corrections" <<endl;
  for (int entry = 0; entry < maxEntries; entry++){
    
    if( entry%1000 == 0 ) std::cout << ">>> Reading entry " << entry << " / " << nEntries << "\r" << std::flush;
    tree->GetEntry(entry);

    if ( !acceptEvent_chRef[entry][chRef] ) continue;

    // -- single channels
    for (int ch = 0; ch < 32; ch++) {
      
      if ( !acceptEvent[entry][ch] ) continue;
      
      float totRatio = (*tot)[channelIdx[ch]]/(*tot)[channelIdx[chRef]] ;
      float totRatioCorr = fitFun_totRatioCorr[ch] -> Eval( totRatio ) - fitFun_totRatioCorr[ch] -> Eval( fitFun_totRatio[ch]->GetParameter(1) ); 
      float deltaT = (*time)[channelIdx[ch]] - (*time)[channelIdx[chRef]];
      
      if ( fabs(deltaT)>10000) continue;   
      if ( fabs(deltaT-totRatioCorr)>10000) continue;   

      h_deltaT_totRatioCorr[ch] -> Fill( deltaT - totRatioCorr);
      p_deltaT_totRatioCorr_vs_t1fine[ch]  -> Fill( (*t1fine)[channelIdx[ch]] , deltaT - totRatioCorr );
      h2_deltaT_totRatioCorr_vs_t1fine[ch] -> Fill( (*t1fine)[channelIdx[ch]] , deltaT - totRatioCorr );

      p_deltaT_totRatioCorr_vs_t1fineRef[ch]  -> Fill( (*t1fine)[channelIdx[chRef]] , deltaT - totRatioCorr );
      h2_deltaT_totRatioCorr_vs_t1fineRef[ch] -> Fill( (*t1fine)[channelIdx[chRef]] , deltaT - totRatioCorr );
    }
  }    




  // -- fourth loop over events to apply amp walk corrections
  cout << "Fourth loop over events to apply phase corrections" <<endl;
  for (int entry = 0; entry < maxEntries; entry++){
    
    if( entry%1000 == 0 ) std::cout << ">>> Reading entry " << entry << " / " << nEntries << "\r" << std::flush;
    tree->GetEntry(entry);

    if ( !acceptEvent_chRef[entry][chRef] ) continue;

    // -- single channels
    for (int ch = 0; ch < 32; ch++) {
      
      if ( !acceptEvent[entry][ch] ) continue;
      
      float deltaT = (*time)[channelIdx[ch]] - (*time)[channelIdx[chRef]];

      float totRatio = (*tot)[channelIdx[ch]]/(*tot)[channelIdx[chRef]] ;
      float totRatioCorr = fitFun_totRatioCorr[ch] -> Eval( totRatio ) - fitFun_totRatioCorr[ch] -> Eval( fitFun_totRatio[ch]->GetParameter(1) ); 
      int bin1  = p_deltaT_totRatioCorr_vs_t1fine[ch]->FindBin( (*t1fine)[channelIdx[ch]]); 
      int bin2 = p_deltaT_totRatioCorr_vs_t1fine[ch]->FindBin( p_deltaT_totRatioCorr_vs_t1fine[ch]->GetMean() );
      float phaseCorr = p_deltaT_totRatioCorr_vs_t1fine[ch] -> GetBinContent(bin1) -  p_deltaT_totRatioCorr_vs_t1fine[ch] -> GetBinContent(bin2);
      
      if ( fabs(deltaT)>10000) continue;   
      if ( fabs(deltaT-totRatioCorr)>10000) continue;   

      h_deltaT_totRatioCorr_phaseCorr[ch] -> Fill( deltaT - totRatioCorr - phaseCorr);

    }
  }    

  
  

  // -- gaus fit deltaT for each channel

  TGraphErrors *g_tRes = new TGraphErrors();
  TGraphErrors *g_tRes_totRatioCorr = new TGraphErrors();
  TGraphErrors *g_tRes_totRatioCorr_phaseCorr = new TGraphErrors();

  map<int,TF1*> fitGaus;
  map<int,TF1*> fitGaus_totRatioCorr;
  map<int,TF1*> fitGaus_totRatioCorr_phaseCorr;
  
  for (int ch = 0; ch < 32; ch++) {
    fitGaus[ch] = new TF1(Form("fitGaus_ch%02d",ch), "gaus",-10000,10000);
    if ( h_deltaT[ch] -> GetEntries() == 0) continue;
    h_deltaT[ch] -> Fit( fitGaus[ch],"QR");
    fitGaus[ch]->SetRange(fitGaus[ch]->GetParameter(1)-2*fitGaus[ch]->GetParameter(2), fitGaus[ch]->GetParameter(1)+2*fitGaus[ch]->GetParameter(2));
    h_deltaT[ch] -> Fit( fitGaus[ch],"QR"); 
    //h_deltaT[ch]-> GetXaxis()->SetRangeUser( h_deltaT[ch]->GetMean() - 7*fitGaus[ch]->GetParameter(2), h_deltaT[ch]->GetMean() + 7*fitGaus[ch]->GetParameter(2));
    h_deltaT[ch]-> GetXaxis()->SetRangeUser( h_deltaT[ch]->GetMean() - 7*h_deltaT[ch]->GetRMS(), h_deltaT[ch]->GetMean() + 7*h_deltaT[ch]->GetRMS());
    g_tRes-> SetPoint( g_tRes->GetN(), ch, fitGaus[ch]->GetParameter(2));
    g_tRes-> SetPointError( g_tRes->GetN()-1, 0, fitGaus[ch]->GetParError(2));
    
    fitGaus_totRatioCorr[ch] = new TF1(Form("fitGaus_totRatioCorr_ch%02d",ch), "gaus",-10000,10000);
    h_deltaT_totRatioCorr[ch] -> Fit( fitGaus_totRatioCorr[ch]);
    fitGaus_totRatioCorr[ch]->SetRange(fitGaus_totRatioCorr[ch]->GetParameter(1)-2*fitGaus_totRatioCorr[ch]->GetParameter(2), fitGaus_totRatioCorr[ch]->GetParameter(1)+2*fitGaus_totRatioCorr[ch]->GetParameter(2));
    h_deltaT_totRatioCorr[ch] -> Fit( fitGaus_totRatioCorr[ch],"QR");
    //    h_deltaT_totRatioCorr[ch]-> GetXaxis()->SetRangeUser( h_deltaT_totRatioCorr[ch]->GetMean() - 7*fitGaus_totRatioCorr[ch]->GetParameter(2), h_deltaT_totRatioCorr[ch]->GetMean() + 7*fitGaus_totRatioCorr[ch]->GetParameter(2));
    h_deltaT_totRatioCorr[ch]-> GetXaxis()->SetRangeUser( h_deltaT_totRatioCorr[ch]->GetMean() - 7*h_deltaT_totRatioCorr[ch]->GetRMS(), h_deltaT_totRatioCorr[ch]->GetMean() + 7*h_deltaT_totRatioCorr[ch]->GetRMS());
    g_tRes_totRatioCorr-> SetPoint( g_tRes_totRatioCorr->GetN(), ch, fitGaus_totRatioCorr[ch]->GetParameter(2));
    g_tRes_totRatioCorr-> SetPointError( g_tRes_totRatioCorr->GetN()-1, 0, fitGaus_totRatioCorr[ch]->GetParError(2));

    fitGaus_totRatioCorr_phaseCorr[ch] = new TF1(Form("fitGaus_totRatioCorr_phaseCorr_ch%02d",ch), "gaus",-10000,10000);
    h_deltaT_totRatioCorr_phaseCorr[ch] -> Fit( fitGaus_totRatioCorr_phaseCorr[ch]);
    fitGaus_totRatioCorr_phaseCorr[ch]->SetRange(fitGaus_totRatioCorr_phaseCorr[ch]->GetParameter(1)-2*fitGaus_totRatioCorr_phaseCorr[ch]->GetParameter(2), fitGaus_totRatioCorr_phaseCorr[ch]->GetParameter(1)+2*fitGaus_totRatioCorr_phaseCorr[ch]->GetParameter(2));
    h_deltaT_totRatioCorr_phaseCorr[ch] -> Fit( fitGaus_totRatioCorr_phaseCorr[ch],"QR");
    h_deltaT_totRatioCorr_phaseCorr[ch]-> GetXaxis()->SetRangeUser( h_deltaT_totRatioCorr_phaseCorr[ch]->GetMean() - 7*fitGaus_totRatioCorr_phaseCorr[ch]->GetParameter(2), h_deltaT_totRatioCorr_phaseCorr[ch]->GetMean() + 7*fitGaus_totRatioCorr_phaseCorr[ch]->GetParameter(2));
    g_tRes_totRatioCorr_phaseCorr-> SetPoint( g_tRes_totRatioCorr_phaseCorr->GetN(), ch, fitGaus_totRatioCorr_phaseCorr[ch]->GetParameter(2));
    g_tRes_totRatioCorr_phaseCorr-> SetPointError( g_tRes_totRatioCorr_phaseCorr->GetN()-1, 0, fitGaus_totRatioCorr_phaseCorr[ch]->GetParError(2));
  }

  // ======  save histograms in a file
  string foutName = Form("plots/analysisSingleChannel_run%d.root",run);
  TFile *fout = new TFile(foutName.c_str(),"recreate");

  for (int ch = 0;  ch < 32; ch++){
	h_totRatio[ch]->Write();
	h_energy[ch]->Write();
	h_deltaT[ch]->Write();
	h_deltaT_totRatioCorr[ch]->Write();
	p_deltaT_vs_totRatio[ch]->Write();
      }
  
  g_tRes->Write();
  g_tRes_totRatioCorr->Write();

  fout->Close();


  gStyle->SetOptFit(1111);
  gStyle->SetOptTitle(0);


  // ======== PLOT 
  
  cout<< "Printing plots ..."<<endl;

  TCanvas *c = new TCanvas("c","c", 700, 600);

  c = new TCanvas("c","c", 700, 600);
  h_nActiveChannels0 -> GetXaxis()->SetTitle("nActiveChannels");
  h_nActiveChannels0->Draw();      
  c->Print(Form("%s/c_nActiveChannels_0.png",plotDir.c_str()));
  c->Print(Form("%s/c_nActiveChannels_0.pdf",plotDir.c_str()));
  delete c;

  c = new TCanvas("c","c", 700, 600);
  h_nActiveChannels1 -> GetXaxis()->SetTitle("nActiveChannels");
  h_nActiveChannels1->Draw();      
  c->Print(Form("%s/c_nActiveChannels_1.png",plotDir.c_str()));
  c->Print(Form("%s/c_nActiveChannels_1.pdf",plotDir.c_str()));
  delete c;


  c = new TCanvas("c","c", 700, 600);
  //c->SetLogy();
  h_energy_chRef-> GetXaxis()->SetTitle("energy [ADC]");
  h_energy_chRef->Draw();      
  c->Print(Form("%s/c_energy_chRef.png",plotDir.c_str()));
  c->Print(Form("%s/c_energy_chRef.pdf",plotDir.c_str()));
  delete c;

  c = new TCanvas("c","c", 700, 600);
  h_deltaT_LR_chRef-> GetXaxis()-> SetRangeUser( h_deltaT_LR_chRef->GetMean() - 7*h_deltaT_LR_chRef->GetRMS(), h_deltaT_LR_chRef->GetMean() + 7*h_deltaT_LR_chRef->GetRMS());
  h_deltaT_LR_chRef-> GetXaxis()-> SetTitle("#DeltaT [ps] ");
  TF1 *ff = new TF1("ff","gaus",-10000,10000);
  h_deltaT_LR_chRef-> Fit(ff,"QRS");
  ff->SetRange( ff->GetParameter(1)-2*ff->GetParameter(2), ff->GetParameter(1)+2*ff->GetParameter(2));
  h_deltaT_LR_chRef-> Fit(ff,"QRS");
  h_deltaT_LR_chRef-> Draw();
  c->Print(Form("%s/c_deltaT_LR_chRef.png",plotDir.c_str()));
  c->Print(Form("%s/c_deltaT_LR_chRef.pdf",plotDir.c_str()));
  delete c;


  c = new TCanvas("c","c", 700, 600);
  h_deltaT_LR-> GetXaxis()-> SetRangeUser( h_deltaT_LR->GetMean() - 7*h_deltaT_LR->GetRMS(), h_deltaT_LR->GetMean() + 7*h_deltaT_LR->GetRMS());
  h_deltaT_LR-> GetXaxis()-> SetTitle("#DeltaT [ps] ");
  h_deltaT_LR-> Fit(ff,"QRS");
  ff->SetRange( ff->GetParameter(1)-2*ff->GetParameter(2), ff->GetParameter(1)+2*ff->GetParameter(2));
  h_deltaT_LR-> Fit(ff,"QRS");
  h_deltaT_LR-> Draw();
  c->Print(Form("%s/c_deltaT_LR.png",plotDir.c_str()));
  c->Print(Form("%s/c_deltaT_LR.pdf",plotDir.c_str()));
  delete c;





  for (int ch = 0;  ch < 32; ch++){   
  
    // -- energy
    c = new TCanvas("c","c", 700, 600);
    //c->SetLogy();
    h_energy[ch]-> GetXaxis()->SetTitle("energy [ADC]");
    h_energy[ch]->Draw();
    c->Print(Form("%s/c_energy_ch%02d.png",plotDir.c_str(),ch));
    c->Print(Form("%s/c_energy_ch%02d.pdf",plotDir.c_str(),ch));
    delete c;

    // -- deltaT
    c = new TCanvas("c","c", 700, 600);
    h_deltaT[ch]-> GetXaxis()->SetTitle("#DeltaT [ps]");
    h_deltaT[ch]->Draw();
    c->Print(Form("%s/c_deltaT_ch%02d.png",plotDir.c_str(),ch));
    c->Print(Form("%s/c_deltaT_ch%02d.pdf",plotDir.c_str(),ch));
    delete c;

    // -- tot Ratio
    c = new TCanvas("c","c", 700, 600);
    h_totRatio[ch]-> GetXaxis()->SetTitle("ToT_{ch}/ToT_{chRef}");
    h_totRatio[ch]->Draw();
    c->Print(Form("%s/c_totRatio_ch%02d.png",plotDir.c_str(),ch));
    c->Print(Form("%s/c_totRatio_ch%02d.pdf",plotDir.c_str(),ch));
    delete c;

    // -- deltaT vs totRatio 
    c = new TCanvas("c","c", 700, 600);
    gStyle->SetOptFit(0);  
    p_deltaT_vs_totRatio[ch]-> SetMarkerStyle(20);
    p_deltaT_vs_totRatio[ch]-> SetMarkerSize(1);
    //p_deltaT_vs_totRatio[ch]-> GetXaxis()-> SetRangeUser(0,2);
    p_deltaT_vs_totRatio[ch]-> GetXaxis()-> SetRangeUser( p_deltaT_vs_totRatio[ch]->GetMean(1) - 3*p_deltaT_vs_totRatio[ch]->GetRMS(1), p_deltaT_vs_totRatio[ch]->GetMean(1) + 3*p_deltaT_vs_totRatio[ch]->GetRMS(1));
    p_deltaT_vs_totRatio[ch]-> GetYaxis()-> SetRangeUser(p_deltaT_vs_totRatio[ch]->GetMean(2) - 3*p_deltaT_vs_totRatio[ch]->GetRMS(2), p_deltaT_vs_totRatio[ch]->GetMean(2) + 3*p_deltaT_vs_totRatio[ch]->GetRMS(2));
    p_deltaT_vs_totRatio[ch]-> GetYaxis()->SetTitle("ToT_{ch}/ToT_{chRef}");
    p_deltaT_vs_totRatio[ch]-> GetYaxis()->SetTitle("#DeltaT [ps]");
    p_deltaT_vs_totRatio[ch]->Draw();
    c->Print(Form("%s/c_deltaT_vs_totRatio_ch%02d.png",plotDir.c_str(),ch));
    c->Print(Form("%s/c_deltaT_vs_totRatio_ch%02d.pdf",plotDir.c_str(),ch));
    delete c;
    gStyle->SetOptFit(1111);  
    
    // -- deltaT corr
    c = new TCanvas("c","c", 700, 600);
    h_deltaT_totRatioCorr[ch]-> GetXaxis()->SetTitle("#DeltaT [ps]");
    h_deltaT_totRatioCorr[ch]->Draw();
    c->Print(Form("%s/c_deltaT_totRatioCorr_ch%02d.png",plotDir.c_str(),ch));
    c->Print(Form("%s/c_deltaT_totRatioCorr_ch%02d.pdf",plotDir.c_str(),ch));
    delete c;

    // -- deltaT corr
    c = new TCanvas("c","c", 700, 600);
    h_deltaT_totRatioCorr_phaseCorr[ch]-> GetXaxis()->SetTitle("#DeltaT [ps]");
    h_deltaT_totRatioCorr_phaseCorr[ch]->Draw();
    c->Print(Form("%s/c_deltaT_totRatioCorr_phaseCorr_ch%02d.png",plotDir.c_str(),ch));
    c->Print(Form("%s/c_deltaT_totRatioCorr_phaseCorr_ch%02d.pdf",plotDir.c_str(),ch));
    delete c;

    // -- deltaT corr vs t1fine
    c = new TCanvas("c","c", 700, 600);
    p_deltaT_totRatioCorr_vs_t1fine[ch]->SetMarkerStyle(20);
    p_deltaT_totRatioCorr_vs_t1fine[ch]->SetMarkerSize(1);
    p_deltaT_totRatioCorr_vs_t1fine[ch]-> GetXaxis()->SetTitle("t1fine");
    p_deltaT_totRatioCorr_vs_t1fine[ch]-> GetYaxis()->SetRangeUser( h2_deltaT_totRatioCorr_vs_t1fine[ch]->GetMean(2) - 500, h2_deltaT_totRatioCorr_vs_t1fine[ch]->GetMean(2) + 500);
    p_deltaT_totRatioCorr_vs_t1fine[ch]->Draw();
    h2_deltaT_totRatioCorr_vs_t1fine[ch]->Draw("colz same");
    p_deltaT_totRatioCorr_vs_t1fine[ch]->Draw("same");

    c->Print(Form("%s/c_deltaT_totRatioCorr_vs_t1fine_ch%02d.png",plotDir.c_str(),ch));
    c->Print(Form("%s/c_deltaT_totRatioCorr_vs_t1fine_ch%02d.pdf",plotDir.c_str(),ch));
    delete c;


    // -- deltaT corr vs t1fine ref channel
    c = new TCanvas("c","c", 700, 600);
    p_deltaT_totRatioCorr_vs_t1fineRef[ch]->SetMarkerStyle(20);
    p_deltaT_totRatioCorr_vs_t1fineRef[ch]->SetMarkerSize(1);
    p_deltaT_totRatioCorr_vs_t1fineRef[ch]-> GetXaxis()->SetTitle("t1fineRef");
    p_deltaT_totRatioCorr_vs_t1fineRef[ch]-> GetYaxis()->SetRangeUser( h2_deltaT_totRatioCorr_vs_t1fineRef[ch]->GetMean(2) - 500, h2_deltaT_totRatioCorr_vs_t1fineRef[ch]->GetMean(2) + 500);
    p_deltaT_totRatioCorr_vs_t1fineRef[ch]->Draw();
    h2_deltaT_totRatioCorr_vs_t1fineRef[ch]->Draw("colz same");
    p_deltaT_totRatioCorr_vs_t1fineRef[ch]->Draw("same");

    c->Print(Form("%s/c_deltaT_totRatioCorr_vs_t1fineRef_ch%02d.png",plotDir.c_str(),ch));
    c->Print(Form("%s/c_deltaT_totRatioCorr_vs_t1fineRef_ch%02d.pdf",plotDir.c_str(),ch));
    delete c;
    
  }
 
  gStyle->SetOptStat(0);

  c = new TCanvas("c","c", 700, 600);
  c->SetGridx();
  c->SetGridy();
  TH2F* hdummy1 = new TH2F("hdummy1","",32,-0.5,31.5,100,75,200);
  hdummy1->GetXaxis()->SetTitle("channel");
  hdummy1->GetYaxis()->SetTitle("#sigma(t_{ch} - t_{chRef} [ps]");
  hdummy1->Draw();
  g_tRes->SetMarkerStyle(20);
  g_tRes->SetMarkerSize(1);
  g_tRes->Draw("psame") ;
  g_tRes_totRatioCorr->SetMarkerStyle(20);
  g_tRes_totRatioCorr->SetLineColor(2);
  g_tRes_totRatioCorr->SetMarkerColor(2);
  g_tRes_totRatioCorr->SetMarkerSize(1);
  g_tRes_totRatioCorr->Draw("psame") ;
  g_tRes_totRatioCorr_phaseCorr->SetMarkerStyle(20);
  g_tRes_totRatioCorr_phaseCorr->SetMarkerColor(4);
  g_tRes_totRatioCorr_phaseCorr->SetLineColor(4);
  g_tRes_totRatioCorr_phaseCorr->SetMarkerSize(1);
  g_tRes_totRatioCorr_phaseCorr->Draw("psame") ;
  c->Print(Form("%s/c_tRes_vs_channel.png",plotDir.c_str()));                                                                                                     
  c->Print(Form("%s/c_tRes_vs_channel.pdf",plotDir.c_str()));                                                                                                     
  delete c;

  c = new TCanvas("c","c", 700, 600);
  c->SetGridx();
  c->SetGridy();
  TH2F* hdummy2 = new TH2F("hdummy2","",32,-0.5,31.5,100,50,200);
  hdummy2->GetXaxis()->SetTitle("channel");
  hdummy2->GetYaxis()->SetTitle("#sigma(t_{ch} - t_{chRef})[ps]");
  hdummy2->Draw();
  g_tRes_totRatioCorr->SetMarkerStyle(20);
  g_tRes_totRatioCorr->SetMarkerSize(1);
  g_tRes_totRatioCorr->Draw("psame") ;
  c->Print(Form("%s/c_tRes_totRatioCorr_vs_channel.png",plotDir.c_str()));                                                                                                     
  c->Print(Form("%s/c_tRes_totRatioCorr_vs_channel.pdf",plotDir.c_str()));                                                                                                     
  delete c;

  c = new TCanvas("c","c", 700, 600);
  c->SetGridx();
  c->SetGridy();
  TH2F* hdummy3 = new TH2F("hdummy3","",32,-0.5,31.5,100,50,200);
  hdummy3->GetXaxis()->SetTitle("channel");
  hdummy3->GetYaxis()->SetTitle("#sigma(t_{ch} - t_{chRef}) [ps]");
  hdummy3->Draw();
  g_tRes_totRatioCorr_phaseCorr->SetMarkerStyle(20);
  g_tRes_totRatioCorr_phaseCorr->SetMarkerSize(1);
  g_tRes_totRatioCorr_phaseCorr->Draw("psame") ;
  c->Print(Form("%s/c_tRes_totRatioCorr_phaseCorr_vs_channel.png",plotDir.c_str()));
  c->Print(Form("%s/c_tRes_totRatioCorr_phaseCorr_vs_channel.pdf",plotDir.c_str()));                                                                                                     



  
 	
}
