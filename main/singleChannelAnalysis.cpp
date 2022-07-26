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

void ilTriangoloNo(float sigma12, float sigma23, float sigma13, std::vector<float> &result) {

    
  float sigma1 = sqrt( 0.5 * ( sigma12*sigma12 + sigma13*sigma13 - sigma23*sigma23) );
  float sigma2 = sqrt( 0.5 * ( sigma12*sigma12 + sigma23*sigma23 - sigma13*sigma13) );
  float sigma3 = sqrt( 0.5 * ( sigma13*sigma13 + sigma23*sigma23 - sigma12*sigma12) );

  result.push_back(sigma1);
  result.push_back(sigma2);
  result.push_back(sigma3);
  
}





// ================================================
int main(int argc, char** argv){
  
  setTDRStyle();
  gErrorIgnoreLevel = kError;  

  if( argc < 2 )
    {
      std::cout << ">>> drawPulseShape::usage:   " << argv[0] << " configFile.cfg" << std::endl;
      return -1;
    }
  
  
  //--- parse the config file
  CfgManager opts;
  opts.ParseConfigFile(argv[1]);
  int debugMode = 0;
  if( argc > 2 ) debugMode = atoi(argv[2]);
  
  std::string runs = opts.GetOpt<std::string>("Input.runs");
  int chRef1 = opts.GetOpt<int>("Input.chRef1");
  int chRef2 = opts.GetOpt<int>("Input.chRef2");
  int useTimeAverage = opts.GetOpt<int>("Input.useTimeAverage"); 
  std::cout<< "Reference channels :  " <<  chRef1 << "  " << chRef2 <<std::endl;
  
  std::vector<unsigned int> channelMapping = opts.GetOpt<std::vector<unsigned int> >("Channels.channelMapping");
  int array = opts.GetOpt<int>("Channels.array"); 


  std::vector<std::string> labelLR = {"L","R"};
  map<std::string, int> chID;  
  for(int iBar = 0; iBar < 16; ++iBar){
    for (auto label : labelLR ){
      if ( label == "L") chID[ Form("bar%02d%s", iBar, label.c_str()) ] = channelMapping[iBar*2+0]+array*64;
      if ( label == "R") chID[ Form("bar%02d%s", iBar, label.c_str()) ] = channelMapping[iBar*2+1]+array*64;
    }
  }

  
  for(int iBar = 0; iBar < 16; ++iBar){
    for (auto label : labelLR ){
      std::string chLabel = Form("bar%02d%s", iBar, label.c_str()); 
      std::cout << iBar << "  " << label << "  " << chID[chLabel] <<   std::endl;
    }
  }

  int maxActiveChannels =  opts.GetOpt<int>("Cuts.maxActiveChannels");
  float minEnergy = opts.GetOpt<int>("Cuts.minEnergy");
  float maxEnergy = 850;
  int mystep2 = opts.GetOpt<int>("Cuts.step2"); 

  
  // --- reading tree
  //------------------------------
  TChain* data = new TChain("data","data");
  
  std::stringstream ss(runs); 
  std::string token;
  while( std::getline(ss,token,',') )
    {
      std::stringstream ss2(token);
      std::string token2;
      int runMin = -1;
      int runMax = -1;
      while( std::getline(ss2,token2,'-') )
	{
	  if( runMin != -1 && runMax == -1 ) runMax = atoi(token2.c_str());
	  if( runMin == -1 ) runMin = atoi(token2.c_str());
	}
      if( runMax == -1 ) runMax = runMin;
      
      for(int run = runMin; run <= runMax; ++run) {
	std::string inFileName = Form("/data1/cmsdaq/tofhir2/h8/reco/%04d/*_e.root",run);
	//std::string inFileName = Form("/data/tofhir2/h8/reco/%04d/*_e.root",run);
	std::cout << ">>> Adding file " << inFileName << std::endl;
	data -> Add(inFileName.c_str());
      }
    }

  //--- define branches
  float step1, step2;
  int channelIdx[128];
  std::vector<float> *tot = 0;
  std::vector<float> *energy = 0;
  std::vector<long long> *time = 0;
  std::vector<unsigned short>* t1fine = 0;
  
  data -> SetBranchStatus("*",0);
  data -> SetBranchStatus("step1",  1); data -> SetBranchAddress("step1",  &step1);
  data -> SetBranchStatus("step2",  1); data -> SetBranchAddress("step2",  &step2);
  data -> SetBranchStatus("channelIdx",  1); data -> SetBranchAddress("channelIdx",  channelIdx);
  data -> SetBranchStatus("tot",    1); data -> SetBranchAddress("tot",       &tot);
  data -> SetBranchStatus("energy", 1); data -> SetBranchAddress("energy", &energy);
  data -> SetBranchStatus("time",   1); data -> SetBranchAddress("time",     &time);
  data -> SetBranchStatus("t1fine",   1); data -> SetBranchAddress("t1fine",     &t1fine);

  int nEntries = data->GetEntries();
  cout << "Number of entries = " << nEntries << endl;
  //  int maxEntries = 200000;
  int maxEntries = nEntries;
  


  // -- book histograms 
  TH1F *h_nActiveChannels0 = new TH1F("h_nActiveChannels0","h_nActiveChannels0",32,-0.5,31.5);
  TH1F *h_nActiveChannels1 = new TH1F("h_nActiveChannels1","h_nActiveChannels1",32,-0.5,31.5);
  
  TH1F *h_energy_chRef = new TH1F("h_energy_chRef","h_energy_chRef",512,0,1024);
  
  map<std::string,TH1F*>      h_energy;
  map<std::string,TH1F*>      h_energyRatio;
  map<std::string,TH2F*>      h2_energyRatio_vs_totRatio;
  map<std::string,TH1F*>      h_deltaT;
  map<std::string,TH1F*>      h_deltaT_energyRatioCorr;
  map<std::string,TH1F*>      h_deltaT_energyRatioCorr_phaseCorr;
  map<std::string,TProfile*>  p_deltaT_vs_energyRatio;
  map<std::string,TH2F*>      h2_deltaT_vs_energyRatio;
  map<std::string,TProfile*>  p_deltaT_energyRatioCorr_vs_t1fine;
  map<std::string,TH2F*>      h2_deltaT_energyRatioCorr_vs_t1fine;
  map<std::string,TProfile*>  p_deltaT_energyRatioCorr_phaseCorr_vs_t1fineRef;
  map<std::string,TH2F*>      h2_deltaT_energyRatioCorr_phaseCorr_vs_t1fineRef;

  map<int,TH1F*>      h_energyRatio_LR;
  map<int,TH1F*>      h_deltaT_LR;
  map<int,TH1F*>      h_deltaT_LR_energyRatioCorr;
  map<int,TH1F*>      h_deltaT_LR_energyRatioCorr_phaseCorr;
  map<int,TProfile*>  p_deltaT_LR_vs_energyRatio;
  map<int,TProfile*>  p_deltaT_LR_energyRatioCorr_vs_t1fine;

  for(int iBar = 0; iBar < 16; ++iBar){        
    
    // L-R
    h_energyRatio_LR[iBar] = new TH1F(Form("h_energyRatio_LR_bar%02d", iBar), Form("h_energyRatio_LR_bar%02d", iBar), 100, 0, 3);
    h_deltaT_LR[iBar] = new TH1F(Form("h_deltaT_LR_bar%02d", iBar), Form("h_deltaT_LR_bar%02d", iBar), 1000, -12000, 12000);
    h_deltaT_LR_energyRatioCorr[iBar] = new TH1F(Form("h_deltaT_LR_energyRatioCorr_bar%02d", iBar), Form("h_deltaT_LR_energyRatioCorr_bar%02d", iBar), 1000, -12000, 12000);
    h_deltaT_LR_energyRatioCorr_phaseCorr[iBar] = new TH1F(Form("h_deltaT_LR_energyRatioCorr_phaseCorr_bar%02d", iBar), Form("h_deltaT_LR_energyRatioCorr_phaseCorr_bar%02d", iBar), 1000, -12000, 12000);
    p_deltaT_LR_vs_energyRatio[iBar] = new TProfile(Form("p_deltaT_LR_vs_energyRatio_bar%02d",iBar), Form("p_deltaT_LR_vs_energyRatio_bar%02d",iBar), 100, 0, 3);
    p_deltaT_LR_energyRatioCorr_vs_t1fine[iBar] = new TProfile(Form("p_deltaT_LR_energyRatioCorr_vs_t1fine_bar%02d",iBar), Form("p_deltaT_LR_energyRatioCorr_vs_t1fine_bar%02d",iBar), 50, 0, 1000);


    for (auto label : labelLR ){
      std::string chLabel = Form("bar%02d%s", iBar, label.c_str());
      
      h_energy[chLabel] = new TH1F(Form("h_energy_%s", chLabel.c_str()) , Form("h_energy_%s", chLabel.c_str()), 512, 0, 1024);
      h_energyRatio[chLabel] = new TH1F(Form("h_energyRatio_%s", chLabel.c_str()) , Form("h_energyRatio_%s", chLabel.c_str()), 100, 0, 3);
      h2_energyRatio_vs_totRatio[chLabel] = new TH2F(Form("h2_energyRatio_vs_totRatio_%s", chLabel.c_str()) , Form("h_energyRatio_vs_totRatio_%s", chLabel.c_str()), 100, 0, 3,100,0,3);
      h_deltaT[chLabel] = new TH1F(Form("h_deltaT_%s", chLabel.c_str()) , Form("h_deltaT_%s", chLabel.c_str()), 1000, -12000, 12000);
      h_deltaT_energyRatioCorr[chLabel] = new TH1F(Form("h_deltaT_energyRatioCorr_%s", chLabel.c_str()) , Form("h_deltaT_energyRatioCorr_%s", chLabel.c_str()), 1000, -12000, 12000);
      h_deltaT_energyRatioCorr_phaseCorr[chLabel] = new TH1F(Form("h_deltaT_energyRatioCorr_phaseCorr_%s", chLabel.c_str()) , Form("h_deltaT_energyRatioCorr_phaseCorr_%s", chLabel.c_str()), 1000, -12000, 12000);
      p_deltaT_vs_energyRatio[chLabel] = new TProfile(Form("p_deltaT_vs_energyRatio_%s", chLabel.c_str()) , Form("p_deltaT_vs_energyRatio_%s", chLabel.c_str()), 100, 0, 3);
      h2_deltaT_vs_energyRatio[chLabel] = new TH2F(Form("h2_deltaT_vs_energyRatio_%s", chLabel.c_str()) , Form("h2_deltaT_vs_energyRatio_%s", chLabel.c_str()), 100, 0, 3, 1000, -12000, 12000);
      p_deltaT_energyRatioCorr_vs_t1fine[chLabel] = new TProfile(Form("p_deltaT_energyRatioCorr_vs_t1fine_%s", chLabel.c_str()) , Form("p_deltaT_energyRatioCorr_vs_t1fine_%s", chLabel.c_str()), 50, 0, 1000);
      h2_deltaT_energyRatioCorr_vs_t1fine[chLabel] = new TH2F(Form("h2_deltaT_energyRatioCorr_vs_t1fine_%s", chLabel.c_str()) , Form("h2_deltaT_energyRatioCorr_vs_t1fine_%s", chLabel.c_str()), 50, 0, 1000, 1000, -12000, 12000);
      p_deltaT_energyRatioCorr_phaseCorr_vs_t1fineRef[chLabel] = new TProfile(Form("p_deltaT_energyRatioCorr_phaseCorr_vs_t1fineRef_%s", chLabel.c_str()) , Form("p_deltaT_energyRatioCorr_phaseCorr_vs_t1fineRef_%s", chLabel.c_str()), 50, 0, 1000);
      h2_deltaT_energyRatioCorr_phaseCorr_vs_t1fineRef[chLabel] = new TH2F(Form("h2_deltaT_energyRatioCorr_phaseCorr_vs_t1fineRef_%s", chLabel.c_str()) , Form("h2_deltaT_energyRatioCorr_phaseCorr_vs_t1fineRef_%s", chLabel.c_str()), 50, 0, 1000, 1000, -12000, 12000);
    }
  }

  TH1F *h_deltaT_LR_chRef = new TH1F("h_deltaT_LR_chRef","h_deltaT_LR_chRef",  1000, -12000, 12000); 

  map <int, map<int, bool> > acceptEvent;
  map<int, bool>  acceptEvent_chRef;

  map<int, int>  nActiveChannels0;
  map<int, int>  nActiveChannels1;

  // -- first loop over events
  cout << "First loop over events to find the mip peak" <<endl;
  for (int entry = 0; entry < maxEntries; entry++){
    
    data->GetEntry(entry);

    if( entry%1000 == 0 ) std::cout << ">>> Reading entry " << entry << " / " << nEntries << "\r" << std::flush;

    if (step2 != mystep2) continue;
    
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

    if (nActiveChannels0[entry] >  maxActiveChannels) continue;
    if (nActiveChannels1[entry] >  maxActiveChannels) continue;


    //-- ref channel
    if ( channelIdx[chRef1] < 0 ) continue;
    if ( channelIdx[chRef2] < 0 ) continue;
    if ( (*tot)[channelIdx[chRef1]]/1000 < -10. || (*tot)[channelIdx[chRef1]]/1000 > 50. ) continue;      
    if ( (*tot)[channelIdx[chRef2]]/1000 < -10. || (*tot)[channelIdx[chRef2]]/1000 > 50. ) continue;      

    float energyRef = 0.5* ((*energy)[channelIdx[chRef1]]+(*energy)[channelIdx[chRef2]] );
    if ( !useTimeAverage) energyRef  = (*energy)[channelIdx[chRef1]];

    h_energy_chRef -> Fill( energyRef );
    

    for(int iBar = 0; iBar < 16; ++iBar){        
      for (auto label : labelLR ){
	std::string chLabel = Form("bar%02d%s", iBar, label.c_str());
	int ch = chID[chLabel]; 
	
	if ( channelIdx[ch] < 0 ) continue;
	if ( (*tot)[channelIdx[ch]]/1000 < -10. || (*tot)[channelIdx[ch]]/1000 > 50. ) continue;
	
	h_energy[chLabel] -> Fill( (*energy)[channelIdx[ch]] );	
      }
    }

  }// -- end first loop over entries


  // -- find min energy
  TF1 *fitLandau_chRef = new TF1("fitLandau_chRef","landau", 0, 1000);
  h_energy_chRef->GetXaxis()->SetRangeUser(200,800);
  int maxbin = h_energy_chRef->GetMaximumBin();
  float peak = h_energy_chRef->GetBinCenter(maxbin);
  fitLandau_chRef->SetRange(peak*0.8, peak*1.2);
  fitLandau_chRef->SetParameter(1,peak);
  fitLandau_chRef->SetParameter(2,0.1*peak);
  h_energy_chRef->Fit("fitLandau_chRef","QR");
  float energyMin_chRef = fitLandau_chRef->GetParameter(1)*0.8;
  h_energy_chRef->GetXaxis()->SetRangeUser(0,1000);

  map<std::string, float> energyMin;
  map<std::string, TF1*> fitLandau;

  for(int iBar = 0; iBar < 16; ++iBar){        
    for (auto label : labelLR ){
      std::string chLabel = Form("bar%02d%s", iBar, label.c_str());
      
      fitLandau[chLabel] = new TF1(Form("fitLandau_%s",chLabel.c_str()),"landau", 0, 1000);    
      h_energy[chLabel]->GetXaxis()->SetRangeUser(minEnergy,800);
      if (chLabel == "bar13L") h_energy[chLabel]->GetXaxis()->SetRangeUser(minEnergy/5,800);
      int maxbin = h_energy[chLabel]->GetMaximumBin();
      float peak = h_energy[chLabel]->GetBinCenter(maxbin);
      fitLandau[chLabel]->SetRange(peak*0.85, peak*1.2);
      fitLandau[chLabel]->SetParameter(1,peak);
      fitLandau[chLabel]->SetParameter(2,0.1*peak);
      h_energy[chLabel]->Fit(fitLandau[chLabel],"QR");
      fitLandau[chLabel]->SetRange(fitLandau[chLabel]->GetParameter(1)*0.85, fitLandau[chLabel]->GetParameter(1)*1.2);  
      energyMin[chLabel] = fitLandau[chLabel]->GetParameter(1)*0.85;
      h_energy[chLabel]->GetXaxis()->SetRangeUser(0,1000);
    }
  }


  // -- second loop over events to get amp walk corrections
  cout << "Second loop over events to get amp walk corrections" <<endl;
  for (int entry = 0; entry < maxEntries; entry++){
    
    if( entry%1000 == 0 ) std::cout << ">>> Reading entry " << entry << " / " << nEntries << "\r" << std::flush;
    data->GetEntry(entry);

    acceptEvent_chRef[entry] = false;

    if (step2 != mystep2) continue;
   
    // -- remove showering events
    if (nActiveChannels0[entry] > maxActiveChannels) continue;
    if (nActiveChannels1[entry] > maxActiveChannels) continue;

    //-- ref channel
    if ( channelIdx[chRef1] < 0 ) continue;
    if ( channelIdx[chRef2] < 0 ) continue;
    if ( (*tot)[channelIdx[chRef1]]/1000 < -10. || (*tot)[channelIdx[chRef1]]/1000 > 50. ) continue;      
    if ( (*tot)[channelIdx[chRef2]]/1000 < -10. || (*tot)[channelIdx[chRef2]]/1000 > 50. ) continue;      
    float energyRef = 0.5*((*energy)[channelIdx[chRef1]]+(*energy)[channelIdx[chRef2]]);
    if ( !useTimeAverage) energyRef  = (*energy)[channelIdx[chRef1]];
    if ( energyRef < energyMin_chRef || energyRef > 850) continue;

    acceptEvent_chRef[entry] = true;

    long long tRef = 0.5*((*time)[channelIdx[chRef1]]+(*time)[channelIdx[chRef2]]);
    if ( !useTimeAverage) tRef  = (*time)[channelIdx[chRef1]];

    // -- single channels
    for(int iBar = 0; iBar < 16; ++iBar){        
      for (auto label : labelLR ){
	std::string chLabel = Form("bar%02d%s", iBar, label.c_str());
	int ch = chID[chLabel]; 

	acceptEvent[entry][ch] = false;

	if ( runs == "5352" && chLabel == "bar00R")  maxEnergy = 600.;
	else if ( runs == "5352" && chLabel == "bar01L")  maxEnergy = 700.;
	else maxEnergy = 850;

	if ( channelIdx[ch] < 0 ) continue;
	if ( (*tot)[channelIdx[ch]]/1000 < -10. || (*tot)[channelIdx[ch]]/1000 > 50. ) continue;
	if ( (*energy)[channelIdx[ch]] < energyMin[chLabel] || (*energy)[channelIdx[ch]] > maxEnergy ) continue;
	
	acceptEvent[entry][ch] = true;
	
	long long deltaT = (*time)[channelIdx[ch]] - tRef;
      
	if ( fabs(deltaT)>10000) continue;
	
	float energyRatio = (*energy)[channelIdx[ch]]/energyRef ;
	float totRatio = (*tot)[channelIdx[ch]]/(*tot)[channelIdx[chRef1]] ;
	
	h_deltaT[chLabel]   -> Fill( deltaT );	
	h_energyRatio[chLabel] -> Fill( energyRatio );	
	h2_energyRatio_vs_totRatio[chLabel] -> Fill( totRatio, energyRatio );	
	p_deltaT_vs_energyRatio[chLabel] -> Fill( energyRatio , deltaT );	
	h2_deltaT_vs_energyRatio[chLabel] -> Fill( energyRatio , deltaT );	
      }

      // tDiff
      int chL = chID[Form("bar%02dL", iBar)];
      int chR = chID[Form("bar%02dR", iBar)];

      if ( acceptEvent[entry][chL]  && acceptEvent[entry][chR]  && acceptEvent_chRef[entry])    {      
	h_energyRatio_LR[iBar]-> Fill( (*energy)[channelIdx[chL]]/(*energy)[channelIdx[chR]] );
	h_deltaT_LR[iBar]-> Fill( (*time)[channelIdx[chL]] - (*time)[channelIdx[chR]] );
	p_deltaT_LR_vs_energyRatio[iBar]-> Fill((*energy)[channelIdx[chL]]/(*energy)[channelIdx[chR]], (*time)[channelIdx[chL]] - (*time)[channelIdx[chR]] );
      }
    
    }// end loop over bars

    // fill deltaT L-R for ref bar
    int ch1 =  0+array*64;
    int ch2 = 31+array*64;
    if ( acceptEvent[entry][ch1]  && acceptEvent[entry][ch2]  && acceptEvent_chRef[entry])    {      
      h_deltaT_LR_chRef ->Fill(  (*time)[channelIdx[chRef1]] - (*time)[channelIdx[chRef2]] );
    }

  }// -- end second loop over entries
  
  
  // ---  amp walk corr
  map<std::string,TF1*> fitFun_energyRatio;
  map<std::string,TF1*> fitFun_energyRatioCorr;

  map<int,TF1*> fitFun_energyRatio_LR;
  map<int,TF1*> fitFun_energyRatioCorr_LR;
  
  for(int iBar = 0; iBar < 16; ++iBar){  

    // L-R
    fitFun_energyRatio_LR[iBar] = new TF1(Form("fitFun_energyRatio_LR_%02d", iBar), "gaus", 0,10);  
    h_energyRatio_LR[iBar] -> Fit(fitFun_energyRatio_LR[iBar],"QR");
    
    fitFun_energyRatioCorr_LR[iBar] = new TF1(Form("fitFun_energyRatioCorr_LR_bar%02d", iBar), "pol3", 0,10);
    fitFun_energyRatioCorr_LR[iBar]->SetRange( fitFun_energyRatio_LR[iBar]->GetParameter(1)-5*fitFun_energyRatio_LR[iBar]->GetParameter(2), fitFun_energyRatio_LR[iBar]->GetParameter(1)+5*fitFun_energyRatio_LR[iBar]->GetParameter(2));
    p_deltaT_LR_vs_energyRatio[iBar] -> Fit(fitFun_energyRatioCorr_LR[iBar],"QRS"); 


    // - single channels 
    for (auto label : labelLR ){
      std::string chLabel = Form("bar%02d%s", iBar, label.c_str());
      int ch = chID[chLabel]; 

      fitFun_energyRatio[chLabel] = new TF1(Form("fitFun_energyRatio_%s",chLabel.c_str()), "gaus", 0,10);  
      h_energyRatio[chLabel] -> Fit(fitFun_energyRatio[chLabel],"QR");

      fitFun_energyRatioCorr[chLabel] = new TF1(Form("fitFun_energyRatioCorr_ch%02d",ch), "pol3", 0,10);
      //fitFun_energyRatioCorr[chLabel]->SetRange( fitFun_energyRatio[chLabel]->GetParameter(1) - 3*fitFun_energyRatio[chLabel]->GetParameter(2), fitFun_energyRatio[chLabel]->GetParameter(1) + 3*fitFun_energyRatio[chLabel]->GetParameter(2) );
      fitFun_energyRatioCorr[chLabel]->SetRange( fitFun_energyRatio[chLabel]->GetParameter(1) - 5*fitFun_energyRatio[chLabel]->GetParameter(2), fitFun_energyRatio[chLabel]->GetParameter(1) + 5*fitFun_energyRatio[chLabel]->GetParameter(2) );
      
      p_deltaT_vs_energyRatio[chLabel] -> Fit(fitFun_energyRatioCorr[chLabel],"QRS");
    }
  }
  
  // -- third loop over events to apply amp walk corrections
  cout << "Third loop over events to apply amp walk corrections" <<endl;
  for (int entry = 0; entry < maxEntries; entry++){
    
    if( entry%1000 == 0 ) std::cout << ">>> Reading entry " << entry << " / " << nEntries << "\r" << std::flush;
    data->GetEntry(entry);

    if ( !acceptEvent_chRef[entry]) continue;

    float energyRef = 0.5*((*energy)[channelIdx[chRef1]]+(*energy)[channelIdx[chRef2]]);
    long long tRef = 0.5*((*time)[channelIdx[chRef1]]+(*time)[channelIdx[chRef2]]);
    if ( !useTimeAverage) {
      energyRef  = (*energy)[channelIdx[chRef1]];
      tRef       = (*time)[channelIdx[chRef1]];
    }

    // -- single channels
    for(int iBar = 0; iBar < 16; ++iBar){        
      for (auto label : labelLR ){
	std::string chLabel = Form("bar%02d%s", iBar, label.c_str());
	int ch = chID[chLabel]; 
	
	if ( !acceptEvent[entry][ch] ) continue;
	
	float energyRatio = (*energy)[channelIdx[ch]]/energyRef;
	float energyRatioCorr = fitFun_energyRatioCorr[chLabel] -> Eval( energyRatio ) - fitFun_energyRatioCorr[chLabel] -> Eval( fitFun_energyRatio[chLabel]->GetParameter(1) ); 
	long long deltaT = (*time)[channelIdx[ch]] - tRef;
	
	if ( fabs(deltaT)>10000) continue;   
	if ( fabs(deltaT-energyRatioCorr)>10000) continue;   
	
	h_deltaT_energyRatioCorr[chLabel] -> Fill( deltaT - energyRatioCorr);
	p_deltaT_energyRatioCorr_vs_t1fine[chLabel]  -> Fill( (*t1fine)[channelIdx[ch]] , deltaT - energyRatioCorr );
	h2_deltaT_energyRatioCorr_vs_t1fine[chLabel] -> Fill( (*t1fine)[channelIdx[ch]] , deltaT - energyRatioCorr );
      } // end loop L,R


      // tDiff L-R
      int chL = chID[Form("bar%02dL", iBar)];
      int chR = chID[Form("bar%02dR", iBar)];

      if ( acceptEvent[entry][chL]  && acceptEvent[entry][chR]  && acceptEvent_chRef[entry])    {      
	float energyRatio = (*energy)[channelIdx[chL]]/(*energy)[channelIdx[chR]];
	float energyRatioCorr = fitFun_energyRatioCorr_LR[iBar] -> Eval( energyRatio ) - fitFun_energyRatioCorr_LR[iBar] -> Eval( fitFun_energyRatio_LR[iBar]->GetParameter(1) ); 
	long long deltaT = (*time)[channelIdx[chL]] - (*time)[channelIdx[chR]];

	h_deltaT_LR_energyRatioCorr[iBar]-> Fill( deltaT - energyRatioCorr);
	p_deltaT_LR_energyRatioCorr_vs_t1fine[iBar]-> Fill( 0.5*( (*t1fine)[channelIdx[chL]]+(*t1fine)[channelIdx[chR]]), deltaT - energyRatioCorr);
      }


    }// end loop over bars
  }    




  // -- fourth loop over events to apply amp walk corrections
  cout << "Fourth loop over events to apply phase corrections" <<endl;
  for (int entry = 0; entry < maxEntries; entry++){
    
    if( entry%1000 == 0 ) std::cout << ">>> Reading entry " << entry << " / " << nEntries << "\r" << std::flush;
    data ->GetEntry(entry);

    if ( !acceptEvent_chRef[entry] ) continue;
    float energyRef = 0.5*((*energy)[channelIdx[chRef1]]+(*energy)[channelIdx[chRef2]]);
    long long tRef = 0.5*((*time)[channelIdx[chRef1]]+(*time)[channelIdx[chRef2]]);
    if ( !useTimeAverage) {
      energyRef  = (*energy)[channelIdx[chRef1]];
      tRef       = (*time)[channelIdx[chRef1]];
    }

    // -- single channels
    for(int iBar = 0; iBar < 16; ++iBar){        
      for (auto label : labelLR ){
	std::string chLabel = Form("bar%02d%s", iBar, label.c_str());
	int ch = chID[chLabel]; 
	
	if ( !acceptEvent[entry][ch] ) continue;
	
	long long deltaT = (*time)[channelIdx[ch]] - tRef;

	//float energyRatio = (*tot)[channelIdx[ch]]/(*tot)[channelIdx[chRef]] ;
	float energyRatio = (*energy)[channelIdx[ch]]/energyRef;
	float energyRatioCorr = fitFun_energyRatioCorr[chLabel] -> Eval( energyRatio ) - fitFun_energyRatioCorr[chLabel] -> Eval( fitFun_energyRatio[chLabel]->GetParameter(1) ); 
	int bin1  = p_deltaT_energyRatioCorr_vs_t1fine[chLabel]->FindBin( (*t1fine)[channelIdx[ch]]) ; 
	int bin2 = p_deltaT_energyRatioCorr_vs_t1fine[chLabel]->FindBin( p_deltaT_energyRatioCorr_vs_t1fine[chLabel]->GetMean() );
	float phaseCorr = p_deltaT_energyRatioCorr_vs_t1fine[chLabel] -> GetBinContent(bin1) -  p_deltaT_energyRatioCorr_vs_t1fine[chLabel] -> GetBinContent(bin2);
      
	if ( fabs(deltaT)>10000) continue;   
	if ( fabs(deltaT-energyRatioCorr)>10000) continue;   
	
	h_deltaT_energyRatioCorr_phaseCorr[chLabel] -> Fill( deltaT - energyRatioCorr - phaseCorr);
	p_deltaT_energyRatioCorr_phaseCorr_vs_t1fineRef[chLabel]  -> Fill( (*t1fine)[channelIdx[chRef2]] , deltaT - energyRatioCorr - phaseCorr);
	h2_deltaT_energyRatioCorr_phaseCorr_vs_t1fineRef[chLabel] -> Fill( (*t1fine)[channelIdx[chRef2]] , deltaT - energyRatioCorr - phaseCorr);
      } // end loop L,R

      
      // tDiff L-R
      int chL = chID[Form("bar%02dL", iBar)];
      int chR = chID[Form("bar%02dR", iBar)];

      if ( acceptEvent[entry][chL]  && acceptEvent[entry][chR]  && acceptEvent_chRef[entry])    {      
	float energyRatio = (*energy)[channelIdx[chL]]/(*energy)[channelIdx[chR]];
	float energyRatioCorr = fitFun_energyRatioCorr_LR[iBar] -> Eval( energyRatio ) - fitFun_energyRatioCorr_LR[iBar] -> Eval( fitFun_energyRatio_LR[iBar]->GetParameter(1) ); 
	long long deltaT = (*time)[channelIdx[chL]] - (*time)[channelIdx[chR]];
	int bin1  = p_deltaT_LR_energyRatioCorr_vs_t1fine[iBar]->FindBin( 0.5 * ( (*t1fine)[channelIdx[chL]]+(*t1fine)[channelIdx[chR]]) ); 
	int bin2 = p_deltaT_LR_energyRatioCorr_vs_t1fine[iBar]->FindBin( p_deltaT_LR_energyRatioCorr_vs_t1fine[iBar]->GetMean() );
	float phaseCorr = p_deltaT_LR_energyRatioCorr_vs_t1fine[iBar] -> GetBinContent(bin1) -  p_deltaT_LR_energyRatioCorr_vs_t1fine[iBar] -> GetBinContent(bin2);

	h_deltaT_LR_energyRatioCorr_phaseCorr[iBar] -> Fill( deltaT - energyRatioCorr - phaseCorr);
      }

    }    // end loop over bars
  }  
  

  // -- gaus fit deltaT for each channel
  map<std::string,TGraphErrors*> g_tRes;
  map<std::string,TGraphErrors*> g_tRes_energyRatioCorr;
  map<std::string,TGraphErrors*> g_tRes_energyRatioCorr_phaseCorr;

  map<std::string,TF1*> fitGaus;
  map<std::string,TF1*> fitGaus_energyRatioCorr;
  map<std::string,TF1*> fitGaus_energyRatioCorr_phaseCorr;

  TGraphErrors *g_tRes_LR = new TGraphErrors();
  TGraphErrors *g_tRes_energyRatioCorr_LR = new TGraphErrors();
  TGraphErrors *g_tRes_energyRatioCorr_phaseCorr_LR = new TGraphErrors();

  map<int,TF1*> fitGaus_LR;
  map<int,TF1*> fitGaus_energyRatioCorr_LR;
  map<int,TF1*> fitGaus_energyRatioCorr_phaseCorr_LR;
  

  // delta T L-R
  std::cout << "time resolution from tDiff(L-R)"<<std::endl;
  for(int iBar = 0; iBar < 16; ++iBar){
    
    if ( h_deltaT_LR[iBar] -> GetEntries() == 0) continue;

    // -- no corr                                                                                                                                                         
    fitGaus_LR[iBar] = new TF1(Form("fitGaus_LR_bar%02d", iBar), "gaus",-10000,10000);                                                                                  
    float fitXmin =  h_deltaT_LR[iBar] -> GetBinCenter( h_deltaT_LR[iBar] -> GetMaximumBin() ) - 200;                                                                     
    float fitXmax =  h_deltaT_LR[iBar] -> GetBinCenter( h_deltaT_LR[iBar] -> GetMaximumBin() ) + 200;                                                                     
    fitGaus_LR[iBar]->SetRange(fitXmin,fitXmax);                                                                                                                          
    h_deltaT_LR[iBar] -> Fit( fitGaus_LR[iBar],"QRL");                                                                                                                    
    fitGaus_LR[iBar]->SetRange(fitGaus_LR[iBar]->GetParameter(1)-2*fitGaus_LR[iBar]->GetParameter(2), fitGaus_LR[iBar]->GetParameter(1)+2*fitGaus_LR[iBar]->GetParameter(2));
    h_deltaT_LR[iBar] -> Fit( fitGaus_LR[iBar],"QRL");
    h_deltaT_LR[iBar]-> GetXaxis()->SetRangeUser( h_deltaT_LR[iBar]->GetMean()-7*h_deltaT_LR[iBar]->GetRMS(), h_deltaT_LR[iBar]->GetMean()+7*h_deltaT_LR[iBar]->GetRMS());
    g_tRes_LR-> SetPoint( g_tRes_LR->GetN(), iBar, fitGaus_LR[iBar]->GetParameter(2));
    g_tRes_LR-> SetPointError( g_tRes_LR->GetN()-1, 0, fitGaus_LR[iBar]->GetParError(2));


    // -- energy corr
    fitGaus_energyRatioCorr_LR[iBar] = new TF1(Form("fitGaus_energyRatioCorr_LR_bar%02d", iBar), "gaus",-10000,10000);
    fitXmin =  h_deltaT_LR_energyRatioCorr[iBar] -> GetBinCenter( h_deltaT_LR_energyRatioCorr[iBar] -> GetMaximumBin() ) - 200;
    fitXmax =  h_deltaT_LR_energyRatioCorr[iBar] -> GetBinCenter( h_deltaT_LR_energyRatioCorr[iBar] -> GetMaximumBin() ) + 200;
    fitGaus_energyRatioCorr_LR[iBar]->SetRange(fitXmin,fitXmax);
    h_deltaT_LR_energyRatioCorr[iBar] -> Fit( fitGaus_energyRatioCorr_LR[iBar],"QRL");
    fitGaus_energyRatioCorr_LR[iBar]->SetRange(fitGaus_energyRatioCorr_LR[iBar]->GetParameter(1)-2*fitGaus_energyRatioCorr_LR[iBar]->GetParameter(2), fitGaus_energyRatioCorr_LR[iBar]->GetParameter(1)+2*fitGaus_energyRatioCorr_LR[iBar]->GetParameter(2));
    h_deltaT_LR_energyRatioCorr[iBar] -> Fit( fitGaus_energyRatioCorr_LR[iBar],"QRL");
    h_deltaT_LR_energyRatioCorr[iBar]-> GetXaxis()->SetRangeUser( h_deltaT_LR_energyRatioCorr[iBar]->GetMean()-7*h_deltaT_LR_energyRatioCorr[iBar]->GetRMS(), h_deltaT_LR_energyRatioCorr[iBar]->GetMean()+7*h_deltaT_LR_energyRatioCorr[iBar]->GetRMS());
    g_tRes_energyRatioCorr_LR-> SetPoint( g_tRes_energyRatioCorr_LR->GetN(), iBar, fitGaus_energyRatioCorr_LR[iBar]->GetParameter(2));
    g_tRes_energyRatioCorr_LR-> SetPointError( g_tRes_energyRatioCorr_LR->GetN()-1, 0, fitGaus_energyRatioCorr_LR[iBar]->GetParError(2));


    // -- energy + phase corr
    fitGaus_energyRatioCorr_phaseCorr_LR[iBar] = new TF1(Form("fitGaus_energyRatioCorr_phaseCorr_LR_bar%02d", iBar), "gaus",-10000,10000);
    fitXmin =  h_deltaT_LR_energyRatioCorr_phaseCorr[iBar] -> GetBinCenter( h_deltaT_LR_energyRatioCorr_phaseCorr[iBar] -> GetMaximumBin() ) - 200;
    fitXmax =  h_deltaT_LR_energyRatioCorr_phaseCorr[iBar] -> GetBinCenter( h_deltaT_LR_energyRatioCorr_phaseCorr[iBar] -> GetMaximumBin() ) + 200;
    fitGaus_energyRatioCorr_phaseCorr_LR[iBar]->SetRange(fitXmin,fitXmax);
    h_deltaT_LR_energyRatioCorr_phaseCorr[iBar] -> Fit( fitGaus_energyRatioCorr_phaseCorr_LR[iBar],"QRL");
    fitGaus_energyRatioCorr_phaseCorr_LR[iBar]->SetRange(fitGaus_energyRatioCorr_phaseCorr_LR[iBar]->GetParameter(1)-2*fitGaus_energyRatioCorr_phaseCorr_LR[iBar]->GetParameter(2), fitGaus_energyRatioCorr_phaseCorr_LR[iBar]->GetParameter(1)+2*fitGaus_energyRatioCorr_phaseCorr_LR[iBar]->GetParameter(2));
    h_deltaT_LR_energyRatioCorr_phaseCorr[iBar] -> Fit( fitGaus_energyRatioCorr_phaseCorr_LR[iBar],"QRL");
    h_deltaT_LR_energyRatioCorr_phaseCorr[iBar]-> GetXaxis()->SetRangeUser( h_deltaT_LR_energyRatioCorr_phaseCorr[iBar]->GetMean()-7*h_deltaT_LR_energyRatioCorr_phaseCorr[iBar]->GetRMS(), h_deltaT_LR_energyRatioCorr_phaseCorr[iBar]->GetMean()+7*h_deltaT_LR_energyRatioCorr_phaseCorr[iBar]->GetRMS());
    g_tRes_energyRatioCorr_phaseCorr_LR-> SetPoint( g_tRes_energyRatioCorr_phaseCorr_LR->GetN(), iBar, fitGaus_energyRatioCorr_phaseCorr_LR[iBar]->GetParameter(2));
    g_tRes_energyRatioCorr_phaseCorr_LR-> SetPointError( g_tRes_energyRatioCorr_phaseCorr_LR->GetN()-1, 0, fitGaus_energyRatioCorr_phaseCorr_LR[iBar]->GetParError(2));
      
  }



  // deltaT ch - Ref
  std::cout << "time resolution from tDiff(ch-Ref)"<<std::endl;
  for (auto label : labelLR ){
    g_tRes[label] = new TGraphErrors();
    g_tRes_energyRatioCorr[label] = new TGraphErrors();
    g_tRes_energyRatioCorr_phaseCorr[label] = new TGraphErrors();
    
    for(int iBar = 0; iBar < 16; ++iBar){        
      std::string chLabel = Form("bar%02d%s", iBar, label.c_str());

      if ( h_deltaT[chLabel] -> GetEntries() == 0) continue;

      // -- no corr
      fitGaus[chLabel] = new TF1(Form("fitGaus_%s",chLabel.c_str()), "gaus",-10000,10000);
      float fitXmin =  h_deltaT[chLabel] -> GetBinCenter( h_deltaT[chLabel] -> GetMaximumBin() ) - 200;
      float fitXmax =  h_deltaT[chLabel] -> GetBinCenter( h_deltaT[chLabel] -> GetMaximumBin() ) + 200;
      fitGaus[chLabel]->SetRange(fitXmin,fitXmax);
      h_deltaT[chLabel] -> Fit( fitGaus[chLabel],"QRL");
      fitGaus[chLabel]->SetRange(fitGaus[chLabel]->GetParameter(1)-2*fitGaus[chLabel]->GetParameter(2), fitGaus[chLabel]->GetParameter(1)+2*fitGaus[chLabel]->GetParameter(2));
      h_deltaT[chLabel] -> Fit( fitGaus[chLabel],"QRL"); 
      h_deltaT[chLabel]-> GetXaxis()->SetRangeUser( h_deltaT[chLabel]->GetMean() - 7*h_deltaT[chLabel]->GetRMS(), h_deltaT[chLabel]->GetMean() + 7*h_deltaT[chLabel]->GetRMS());
      g_tRes[label]-> SetPoint( g_tRes[label]->GetN(), iBar, fitGaus[chLabel]->GetParameter(2));
      g_tRes[label]-> SetPointError( g_tRes[label]->GetN()-1, 0, fitGaus[chLabel]->GetParError(2));
      
      // -- energy corr
      fitGaus_energyRatioCorr[chLabel] = new TF1(Form("fitGaus_energyRatioCorr_%s",chLabel.c_str()), "gaus",-10000,10000);
      fitXmin =  h_deltaT_energyRatioCorr[chLabel] -> GetBinCenter( h_deltaT_energyRatioCorr[chLabel] -> GetMaximumBin() ) - 200;
      fitXmax =  h_deltaT_energyRatioCorr[chLabel] -> GetBinCenter( h_deltaT_energyRatioCorr[chLabel] -> GetMaximumBin() ) + 200;
      fitGaus_energyRatioCorr[chLabel]->SetRange(fitXmin,fitXmax); 
      h_deltaT_energyRatioCorr[chLabel] -> Fit( fitGaus_energyRatioCorr[chLabel],"QRL");
      fitGaus_energyRatioCorr[chLabel]->SetRange(fitGaus_energyRatioCorr[chLabel]->GetParameter(1)-2*fitGaus_energyRatioCorr[chLabel]->GetParameter(2), fitGaus_energyRatioCorr[chLabel]->GetParameter(1)+2*fitGaus_energyRatioCorr[chLabel]->GetParameter(2));
      h_deltaT_energyRatioCorr[chLabel] -> Fit( fitGaus_energyRatioCorr[chLabel],"QRL");
      h_deltaT_energyRatioCorr[chLabel]-> GetXaxis()->SetRangeUser( h_deltaT_energyRatioCorr[chLabel]->GetMean() - 7*h_deltaT_energyRatioCorr[chLabel]->GetRMS(), h_deltaT_energyRatioCorr[chLabel]->GetMean() + 7*h_deltaT_energyRatioCorr[chLabel]->GetRMS());
      g_tRes_energyRatioCorr[label]-> SetPoint( g_tRes_energyRatioCorr[label]->GetN(), iBar, fitGaus_energyRatioCorr[chLabel]->GetParameter(2));
      g_tRes_energyRatioCorr[label]-> SetPointError( g_tRes_energyRatioCorr[label]->GetN()-1, 0, fitGaus_energyRatioCorr[chLabel]->GetParError(2));
      
      // -- energy + phase corr
      fitGaus_energyRatioCorr_phaseCorr[chLabel] = new TF1(Form("fitGaus_energyRatioCorr_phaseCorr_%s",chLabel.c_str()), "gaus",-10000,10000);
      fitXmin =  h_deltaT_energyRatioCorr_phaseCorr[chLabel] -> GetBinCenter( h_deltaT_energyRatioCorr_phaseCorr[chLabel] -> GetMaximumBin() ) - 200;
      fitXmax =  h_deltaT_energyRatioCorr_phaseCorr[chLabel] -> GetBinCenter( h_deltaT_energyRatioCorr_phaseCorr[chLabel] -> GetMaximumBin() ) + 200;
      fitGaus_energyRatioCorr_phaseCorr[chLabel]->SetRange(fitXmin,fitXmax); 
      h_deltaT_energyRatioCorr_phaseCorr[chLabel] -> Fit( fitGaus_energyRatioCorr_phaseCorr[chLabel],"QRL");
      fitGaus_energyRatioCorr_phaseCorr[chLabel]->SetRange(fitGaus_energyRatioCorr_phaseCorr[chLabel]->GetParameter(1)-2*fitGaus_energyRatioCorr_phaseCorr[chLabel]->GetParameter(2), fitGaus_energyRatioCorr_phaseCorr[chLabel]->GetParameter(1)+2*fitGaus_energyRatioCorr_phaseCorr[chLabel]->GetParameter(2));
      h_deltaT_energyRatioCorr_phaseCorr[chLabel] -> Fit( fitGaus_energyRatioCorr_phaseCorr[chLabel],"QRL");
      h_deltaT_energyRatioCorr_phaseCorr[chLabel]-> GetXaxis()->SetRangeUser( h_deltaT_energyRatioCorr_phaseCorr[chLabel]->GetMean() - 7*fitGaus_energyRatioCorr_phaseCorr[chLabel]->GetParameter(2), h_deltaT_energyRatioCorr_phaseCorr[chLabel]->GetMean() + 7*fitGaus_energyRatioCorr_phaseCorr[chLabel]->GetParameter(2));
      g_tRes_energyRatioCorr_phaseCorr[label]-> SetPoint( g_tRes_energyRatioCorr_phaseCorr[label]->GetN(), iBar, fitGaus_energyRatioCorr_phaseCorr[chLabel]->GetParameter(2));
      g_tRes_energyRatioCorr_phaseCorr[label]-> SetPointError( g_tRes_energyRatioCorr_phaseCorr[label]->GetN()-1, 0, fitGaus_energyRatioCorr_phaseCorr[chLabel]->GetParError(2));
  
    }
  }
  
  
  
  // triangulation
  std::cout << "Triangulation ..." << std::endl;
  TGraphErrors *g_tRes_L = new TGraphErrors();
  TGraphErrors *g_tRes_R = new TGraphErrors();
  TGraphErrors *g_tRes_chRef = new TGraphErrors();
 
  for (int iBar = 0 ; iBar < 16; iBar++){

    if (h_deltaT_LR_energyRatioCorr_phaseCorr[iBar] -> GetEntries() == 0) continue;
    if (h_deltaT_energyRatioCorr_phaseCorr[ Form("bar%02dR", iBar)] -> GetEntries() == 0) continue;
    if (h_deltaT_energyRatioCorr_phaseCorr[ Form("bar%02dL", iBar)] -> GetEntries() == 0) continue;

    
    float tRes_L_R = g_tRes_energyRatioCorr_phaseCorr_LR->Eval(iBar);
    float tRes_L_chRef = g_tRes_energyRatioCorr_phaseCorr["L"]->Eval(iBar);
    float tRes_R_chRef = g_tRes_energyRatioCorr_phaseCorr["R"]->Eval(iBar);

    std::vector<float> tRes ;
    tRes.clear();
    ilTriangoloNo(tRes_L_R,tRes_R_chRef,tRes_L_chRef, tRes);

    g_tRes_L -> SetPoint( g_tRes_L->GetN(), iBar, tRes[0]);
    g_tRes_R -> SetPoint( g_tRes_R->GetN(), iBar, tRes[1]);
    g_tRes_chRef -> SetPoint( g_tRes_chRef->GetN(), iBar, tRes[2]);
  }







  // ======  save histograms in a file
  string foutName = Form("plots/analysisSingleChannel_runs%s.root",runs.c_str());
  if (useTimeAverage) foutName = Form("plots/analysisSingleChannel_runs%s_timeAverage.root",runs.c_str());
  
  TFile *fout = new TFile(foutName.c_str(),"recreate");

  for (auto label : labelLR ){
    for(int iBar = 0; iBar < 16; ++iBar){        
      std::string chLabel = Form("bar%02d%s", iBar, label.c_str());
      h_energyRatio[chLabel]->Write();
      h2_energyRatio_vs_totRatio[chLabel]->Write();
      h_energy[chLabel]->Write();
      h_deltaT[chLabel]->Write();
      h_deltaT_energyRatioCorr[chLabel]->Write();
      p_deltaT_vs_energyRatio[chLabel]->Write();
    }
    
    g_tRes[label]->Write(Form("g_tRes_%s",label.c_str()));
    g_tRes_energyRatioCorr[label]->Write(Form("g_tRes_energyRatioCorr_%s",label.c_str()));
    g_tRes_energyRatioCorr_phaseCorr[label]->Write( Form("g_tRes_energyRatioCorr_phaseCorr_%s",label.c_str()));
  }
  
  fout->Close();


  gStyle->SetOptFit(1111);
  gStyle->SetOptTitle(0);

  // ======== PLOT 
  std::string plotDir(Form("/var/www/html/TOFHIR2B/MTDTB_CERN_June22/analysisSingleChannel/%s/",runs.c_str() ));
  if (useTimeAverage) plotDir = Form("/var/www/html/TOFHIR2B/MTDTB_CERN_June22/analysisSingleChannel/%s_timeAverage/",runs.c_str() );

  system(Form("mkdir -p %s",plotDir.c_str()));  

  cout<< "Printing plots ..."<<endl;

  TCanvas *c;

  c = new TCanvas("c","c", 800, 600);
  h_nActiveChannels0 -> GetXaxis()->SetTitle("nActiveChannels");
  h_nActiveChannels0->Draw(); 
  TLine* line = new TLine(maxActiveChannels,0.,maxActiveChannels,h_nActiveChannels0 ->GetMaximum());
  line -> SetLineWidth(1);
  line -> SetLineStyle(7);
  line -> Draw("same");     
  c->Print(Form("%s/c_nActiveChannels_0.png",plotDir.c_str()));
  c->Print(Form("%s/c_nActiveChannels_0.pdf",plotDir.c_str()));
  delete c;

  c = new TCanvas("c","c", 800, 600);
  h_nActiveChannels1 -> GetXaxis()->SetTitle("nActiveChannels");
  h_nActiveChannels1->Draw();
  line -> Draw("same");           
  c->Print(Form("%s/c_nActiveChannels_1.png",plotDir.c_str()));
  c->Print(Form("%s/c_nActiveChannels_1.pdf",plotDir.c_str()));
  delete c;


  c = new TCanvas("c","c", 800, 600);
  //c->SetLogy();
  h_energy_chRef-> GetXaxis()->SetTitle("energy [ADC]");
  h_energy_chRef->Draw();      
  c->Print(Form("%s/c_energy_chRef.png",plotDir.c_str()));
  c->Print(Form("%s/c_energy_chRef.pdf",plotDir.c_str()));
  delete c;

  c = new TCanvas("c","c", 800, 600);
  h_deltaT_LR_chRef-> GetXaxis()-> SetRangeUser( h_deltaT_LR_chRef->GetMean()-7*h_deltaT_LR_chRef->GetRMS(), h_deltaT_LR_chRef->GetMean()+7*h_deltaT_LR_chRef->GetRMS());
  h_deltaT_LR_chRef-> GetXaxis()-> SetTitle("#Deltat [ps] ");
  TF1 *ff = new TF1("ff","gaus",-10000,10000);
  h_deltaT_LR_chRef-> Fit(ff,"QRS");
  ff->SetRange( ff->GetParameter(1)-2*ff->GetParameter(2), ff->GetParameter(1)+2*ff->GetParameter(2));
  h_deltaT_LR_chRef-> Fit(ff,"QRS");
  h_deltaT_LR_chRef-> Draw();
  c->Print(Form("%s/c_deltaT_LR_chRef.png",plotDir.c_str()));
  c->Print(Form("%s/c_deltaT_LR_chRef.pdf",plotDir.c_str()));
  delete c;

  for(int iBar = 0; iBar < 16; ++iBar){
    c = new TCanvas("c","c", 800, 600);
    h_deltaT_LR[iBar]-> GetXaxis()-> SetRangeUser(h_deltaT_LR[iBar]->GetMean()-7*h_deltaT_LR[iBar]->GetRMS(), h_deltaT_LR[iBar]->GetMean()+7*h_deltaT_LR[iBar]->GetRMS());
    h_deltaT_LR[iBar]-> GetXaxis()-> SetTitle("#Deltat [ps] ");
    h_deltaT_LR[iBar]-> Fit(ff,"QRS");
    ff->SetRange( ff->GetParameter(1)-2*ff->GetParameter(2), ff->GetParameter(1)+2*ff->GetParameter(2));
    h_deltaT_LR[iBar]-> Fit(ff,"QRS");
    h_deltaT_LR[iBar]-> Draw();
    c->Print(Form("%s/c_deltaT_LR_bar%02d.png",plotDir.c_str(), iBar) );
    c->Print(Form("%s/c_deltaT_LR_bar%02d.pdf",plotDir.c_str(), iBar) );
    delete c;
  }

  
  
  for (auto label : labelLR ){
    for(int iBar = 0; iBar < 16; ++iBar){        
      std::string chLabel = Form("bar%02d%s", iBar, label.c_str());
      
      // -- energy
      c = new TCanvas("c","c", 800, 600);
      //c->SetLogy();
      h_energy[chLabel]-> GetXaxis()->SetTitle("energy [ADC]");
      h_energy[chLabel]->Draw();
      TLine* line = new TLine(energyMin[chLabel],0.,energyMin[chLabel],h_energy[chLabel]->GetMaximum());
      line -> SetLineWidth(1);
      line -> SetLineStyle(7);
      line -> Draw("same");
      TLine* line2 = new TLine(maxEnergy,0.,maxEnergy,h_energy[chLabel]->GetMaximum());
      line2 -> SetLineWidth(1);
      line2 -> SetLineStyle(7);
      line2 -> Draw("same");
      c->Print(Form("%s/c_energy_%s.png",plotDir.c_str(),chLabel.c_str()));
      c->Print(Form("%s/c_energy_%s.pdf",plotDir.c_str(),chLabel.c_str()));
      delete c;
      
      // -- deltaT
      c = new TCanvas("c","c", 800, 600);
      h_deltaT[chLabel]-> GetXaxis()->SetTitle("#Deltat [ps]");
      h_deltaT[chLabel]->Draw();
      c->Print(Form("%s/c_deltaT_%s.png",plotDir.c_str(),chLabel.c_str()));
      c->Print(Form("%s/c_deltaT_%s.pdf",plotDir.c_str(),chLabel.c_str()));
      delete c;
      
      // -- tot Ratio
      c = new TCanvas("c","c", 800, 600);
      h_energyRatio[chLabel]-> GetXaxis()->SetTitle("E_{ch}/E_{chRef}");
      h_energyRatio[chLabel]->Draw();
      c->Print(Form("%s/c_energyRatio_%s.png",plotDir.c_str(),chLabel.c_str()));
      c->Print(Form("%s/c_energyRatio_%s.pdf",plotDir.c_str(),chLabel.c_str()));
      delete c;
      
      // -- deltaT vs energyRatio 
      c = new TCanvas("c","c", 800, 600);
      gStyle->SetOptFit(0);  
      p_deltaT_vs_energyRatio[chLabel]-> SetMarkerStyle(20);
      p_deltaT_vs_energyRatio[chLabel]-> SetMarkerSize(1);
      p_deltaT_vs_energyRatio[chLabel]-> GetXaxis()-> SetRangeUser( p_deltaT_vs_energyRatio[chLabel]->GetMean(1) - 3*p_deltaT_vs_energyRatio[chLabel]->GetRMS(1), p_deltaT_vs_energyRatio[chLabel]->GetMean(1) + 3*p_deltaT_vs_energyRatio[chLabel]->GetRMS(1));
      p_deltaT_vs_energyRatio[chLabel]-> GetYaxis()-> SetRangeUser(p_deltaT_vs_energyRatio[chLabel]->GetMean(2) - 3*p_deltaT_vs_energyRatio[chLabel]->GetRMS(2), p_deltaT_vs_energyRatio[chLabel]->GetMean(2) + 3*p_deltaT_vs_energyRatio[chLabel]->GetRMS(2));
      p_deltaT_vs_energyRatio[chLabel]-> GetYaxis()->SetTitle("E_{ch}/E_{chRef}");
      p_deltaT_vs_energyRatio[chLabel]-> GetYaxis()->SetTitle("#DeltaT [ps]");
      p_deltaT_vs_energyRatio[chLabel]->Draw();
      h2_deltaT_vs_energyRatio[chLabel]->Draw("colz same");
      p_deltaT_vs_energyRatio[chLabel]->Draw("same");
      c->Print(Form("%s/c_deltaT_vs_energyRatio_%s.png",plotDir.c_str(),chLabel.c_str()));
      c->Print(Form("%s/c_deltaT_vs_energyRatio_%s.pdf",plotDir.c_str(),chLabel.c_str()));
      delete c;
      gStyle->SetOptFit(1111);  
      
      // -- deltaT corr
      c = new TCanvas("c","c", 800, 600);
      h_deltaT_energyRatioCorr[chLabel]-> GetXaxis()->SetTitle("#Deltat [ps]");
      h_deltaT_energyRatioCorr[chLabel]->Draw();
      c->Print(Form("%s/c_deltaT_energyRatioCorr_%s.png",plotDir.c_str(),chLabel.c_str()));
      c->Print(Form("%s/c_deltaT_energyRatioCorr_%s.pdf",plotDir.c_str(),chLabel.c_str()));
      delete c;
      
      // -- deltaT energy+phase corr
      c = new TCanvas("c","c", 800, 600);
      h_deltaT_energyRatioCorr_phaseCorr[chLabel]-> GetXaxis()->SetTitle("#Deltat [ps]");
      h_deltaT_energyRatioCorr_phaseCorr[chLabel]->Draw();
      c->Print(Form("%s/c_deltaT_energyRatioCorr_phaseCorr_%s.png",plotDir.c_str(),chLabel.c_str()));
      c->Print(Form("%s/c_deltaT_energyRatioCorr_phaseCorr_%s.pdf",plotDir.c_str(),chLabel.c_str()));
      delete c;

      // -- deltaT corr vs t1fine
      c = new TCanvas("c","c", 800, 600);
      p_deltaT_energyRatioCorr_vs_t1fine[chLabel]->SetMarkerStyle(20);
      p_deltaT_energyRatioCorr_vs_t1fine[chLabel]->SetMarkerSize(1);
      p_deltaT_energyRatioCorr_vs_t1fine[chLabel]-> GetXaxis()->SetTitle("t1fine");
      p_deltaT_energyRatioCorr_vs_t1fine[chLabel]-> GetYaxis()->SetRangeUser( h2_deltaT_energyRatioCorr_vs_t1fine[chLabel]->GetMean(2) - 300, h2_deltaT_energyRatioCorr_vs_t1fine[chLabel]->GetMean(2) + 300);
      p_deltaT_energyRatioCorr_vs_t1fine[chLabel]->Draw();
      h2_deltaT_energyRatioCorr_vs_t1fine[chLabel]->Draw("colz same");
      p_deltaT_energyRatioCorr_vs_t1fine[chLabel]->Draw("same");
      
      c->Print(Form("%s/c_deltaT_energyRatioCorr_vs_t1fine_%s.png",plotDir.c_str(),chLabel.c_str()));
      c->Print(Form("%s/c_deltaT_energyRatioCorr_vs_t1fine_%s.pdf",plotDir.c_str(),chLabel.c_str()));
      delete c;
      
      
      // -- deltaT corr vs t1fine ref channel
      c = new TCanvas("c","c", 800, 600);
      p_deltaT_energyRatioCorr_phaseCorr_vs_t1fineRef[chLabel]->SetMarkerStyle(20);
      p_deltaT_energyRatioCorr_phaseCorr_vs_t1fineRef[chLabel]->SetMarkerSize(1);
      p_deltaT_energyRatioCorr_phaseCorr_vs_t1fineRef[chLabel]-> GetXaxis()->SetTitle("t1fine_{chRef}");
      p_deltaT_energyRatioCorr_phaseCorr_vs_t1fineRef[chLabel]-> GetYaxis()->SetRangeUser( h2_deltaT_energyRatioCorr_phaseCorr_vs_t1fineRef[chLabel]->GetMean(2) - 300, h2_deltaT_energyRatioCorr_phaseCorr_vs_t1fineRef[chLabel]->GetMean(2) + 300);
      p_deltaT_energyRatioCorr_phaseCorr_vs_t1fineRef[chLabel]->Draw();
      h2_deltaT_energyRatioCorr_phaseCorr_vs_t1fineRef[chLabel]->Draw("colz same");
      p_deltaT_energyRatioCorr_phaseCorr_vs_t1fineRef[chLabel]->Draw("same");
      
      c->Print(Form("%s/c_deltaT_energyRatioCorr_phaseCorr_vs_t1fineRef_%s.png",plotDir.c_str(),chLabel.c_str()));
      c->Print(Form("%s/c_deltaT_energyRatioCorr_phaseCorr_vs_t1fineRef_%s.pdf",plotDir.c_str(),chLabel.c_str()));
      delete c;
      
    }
  }
  
  gStyle->SetOptStat(0);
  
  // -- no corr
  float ymin = 70;
  float ymax = 140;

  //if (useTimeAverage){
  //  ymin = 60;
  //  ymax = 120;
  //}

  c = new TCanvas("c","c", 800, 600);
  c->SetGridx();
  c->SetGridy();
  TH2F* hdummy1 = new TH2F("hdummy1","",16,-0.5,15.5,100,30,200);
  hdummy1->GetXaxis()->SetTitle("bar");
  hdummy1->GetYaxis()->SetTitle("#sigma(t_{ch} - t_{ref} [ps]");
  hdummy1->Draw();
  for (auto label : labelLR ){   
    g_tRes[label]->SetMarkerStyle(20);
    if (label == "R") g_tRes[label]->SetMarkerStyle(24);
    g_tRes[label]->SetMarkerSize(1);
    g_tRes[label]->Draw("psame") ;
    g_tRes_energyRatioCorr[label]->SetMarkerColor(2);
    g_tRes_energyRatioCorr[label]->SetLineColor(2);
    g_tRes_energyRatioCorr[label]->SetMarkerStyle(20);
    if (label == "R") g_tRes_energyRatioCorr[label]->SetMarkerStyle(24);
    g_tRes_energyRatioCorr[label]->SetMarkerSize(1);
    g_tRes_energyRatioCorr[label]->Draw("psame") ;
  }
  c->Print(Form("%s/c_tRes_vs_bar.png",plotDir.c_str()));                                                                                                     
  c->Print(Form("%s/c_tRes_vs_bar.pdf",plotDir.c_str()));                                                                                                     
  delete c;
  
  
  // -- energy corr
  c = new TCanvas("c","c", 800, 600);
  c->SetGridx();
  c->SetGridy();
  TH2F* hdummy2 = new TH2F("hdummy2","",16,-0.5,15.5,100,ymin,ymax);
  hdummy2->GetXaxis()->SetTitle("bar");
  hdummy2->GetYaxis()->SetTitle("#sigma(t_{ch} - t_{ref} [ps]");
  hdummy2->Draw();
  for (auto label : labelLR ){   
    g_tRes_energyRatioCorr[label]->SetMarkerColor(2);
    g_tRes_energyRatioCorr[label]->SetLineColor(2);
    g_tRes_energyRatioCorr[label]->SetMarkerStyle(20);
    if (label == "R") g_tRes_energyRatioCorr[label]->SetMarkerStyle(24);
    g_tRes_energyRatioCorr[label]->SetMarkerSize(1);
    g_tRes_energyRatioCorr[label]->Draw("psame") ;
  }
  c->Print(Form("%s/c_tRes_energyRatioCorr_vs_bar.png",plotDir.c_str()));
  c->Print(Form("%s/c_tRes_energyRatioCorr_vs_bar.pdf",plotDir.c_str()));
  delete c;
  
    
  // -- energy+phase corr
  c = new TCanvas("c","c", 800, 600);
  c->SetGridx();
  c->SetGridy();
  TH2F* hdummy3 = new TH2F("hdummy3","",16,-0.5,15.5,100,ymin,ymax);
  hdummy3->GetXaxis()->SetTitle("bar");
  hdummy3->GetYaxis()->SetTitle("#sigma(t_{ch} - t_{ref} [ps]");
  hdummy3->Draw();
  for (auto label : labelLR ){   
    g_tRes_energyRatioCorr_phaseCorr[label]->SetMarkerColor(4);
    g_tRes_energyRatioCorr_phaseCorr[label]->SetLineColor(4);
    g_tRes_energyRatioCorr_phaseCorr[label]->SetMarkerStyle(20);
    if (label == "R") g_tRes_energyRatioCorr_phaseCorr[label]->SetMarkerStyle(24);
    g_tRes_energyRatioCorr_phaseCorr[label]->SetMarkerSize(1);
    g_tRes_energyRatioCorr_phaseCorr[label]->Draw("psame") ;
  }
  c->Print(Form("%s/c_tRes_energyRatioCorr_phaseCorr_vs_bar.png",plotDir.c_str()));
  c->Print(Form("%s/c_tRes_energyRatioCorr_phaseCorr_vs_bar.pdf",plotDir.c_str()));
  delete c;



  // -- tRes of L, R, chRef after triangulation
  c = new TCanvas("c","c", 800, 600);
  c->SetGridx();
  c->SetGridy();
  TH2F* hdummy4 = new TH2F("hdummy4","",16,-0.5,15.5,100,0,120);
  hdummy4->GetXaxis()->SetTitle("bar");
  hdummy4->GetYaxis()->SetTitle("#sigma_t [ps]");
  hdummy4->Draw();
  g_tRes_L ->SetMarkerStyle(20);
  g_tRes_R ->SetMarkerStyle(24);
  g_tRes_chRef ->SetMarkerStyle(21);
  g_tRes_L->Draw("psame") ;
  g_tRes_R->Draw("psame") ;
  g_tRes_chRef->Draw("psame") ;

  TLegend *leg = new TLegend(0.20, 0.20, 0.50, 0.35);
  leg->SetBorderSize(0);
  leg->AddEntry(g_tRes_L, "L", "P");
  leg->AddEntry(g_tRes_R, "R", "P");
  leg->AddEntry(g_tRes_chRef, "chRef", "P");
  leg->Draw("same");

  c->Print(Form("%s/c_tRes.png",plotDir.c_str()));
  c->Print(Form("%s/c_tRes.pdf",plotDir.c_str()));
  delete c;
  
}
  
