#include "interface/TOFHIRThresholdZero.h"
#include "interface/AnalysisUtils.h"
#include "interface/FitUtils.h"
#include "interface/SetTDRStyle.h"
#include "CfgManager/interface/CfgManager.h"
#include "CfgManager/interface/CfgManagerT.h"

#include <iostream>
#include <fstream>
#include <vector>
#include <map>
#include <time.h>
#include <stdio.h>
#include <sys/stat.h>
#include <cmath>

#include "TFile.h"
#include "TChain.h"
#include "TH1F.h"
#include "TProfile.h"
#include "TProfile2D.h"
#include "TGraphErrors.h"
#include "TF1.h"
#include "TCanvas.h"
#include "TLatex.h"
#include "TLine.h"
#include "TRandom3.h"
#include "TMath.h"




double fitEfficiencyVsPosition(double* x, double* par)
{
  double t = x[0];
  
  double center= par[0];
  double width = par[1];
  double baseline= par[2];
  double max     = par[3];
  double sigma_x   = par[4];
  
  double f;
  double edge1 = center-width/2;
  double edge2 = center+width/2;
  
  if ( t <= center)
    {
      f = baseline + max/2*(erf( (t-edge1) / (sqrt(2)*sigma_x)) + 1);
    }
  if (t > center)
    {
      f = baseline + max/2*(erf((-t+edge2) / (sqrt(2)*sigma_x)) + 1);
    }
  
  
  return f;
}




int main(int argc, char** argv)
{
  setTDRStyle();

  //--- parse the config file
  CfgManager opts;
  opts.ParseConfigFile(argv[1]);


  //--- open files and make the tree chain
  std::string inputDir = opts.GetOpt<std::string>("Input.inputDir");
  std::string fileBaseName = opts.GetOpt<std::string>("Input.fileBaseName");
  std::string runs = opts.GetOpt<std::string>("Input.runs");
  int maxEntries = opts.GetOpt<int>("Input.maxEntries");

  std::string discCalibrationFile = opts.GetOpt<std::string>("Input.discCalibration");
  TOFHIRThresholdZero thrZero(discCalibrationFile,1);

  TChain* tree = new TChain("data","data");
  
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
    
      for(int run = runMin; run <= runMax; ++run)
	{
	  std::string fileName = Form("%s/%s%05d_e.root",inputDir.c_str(),fileBaseName.c_str(),run);
	  	  
	  // -- check if tree contains track info
	  bool treeHasTrackInfo = true;
	  TFile *f = TFile::Open(fileName.c_str());
	  TTree *tmpTree = f->Get<TTree>("data");
	  if ( (tmpTree->GetBranch("x_dut")) == NULL )  {
	    treeHasTrackInfo = false;
	    std::cout << "File " << fileName << "  has no track info --> skipping run " << run << std::endl;
	  }
	  delete tmpTree;
	  
	  if (treeHasTrackInfo) {
	    std::cout << ">>> Adding file " << fileName << std::endl;
	    tree -> Add(fileName.c_str());
	  }
	}
    }


  //--- define channels (read mapping from the configuration file)
  std::vector<unsigned int> channelMapping = opts.GetOpt<std::vector<unsigned int> >("Channels.channelMapping");

  int chL[16];
  int chR[16];

  for(unsigned int iBar = 0; iBar < channelMapping.size()/2; ++iBar){
    if(opts.GetOpt<int>("Channels.array")==0){
      chL[iBar] = channelMapping[iBar*2+0];
      chR[iBar] = channelMapping[iBar*2+1];
    }
    if(opts.GetOpt<int>("Channels.array")==1){
      chL[iBar] = channelMapping[iBar*2+0]+64;
      chR[iBar] = channelMapping[iBar*2+1]+64;
    }
    //std::cout << "Bar: " << iBar << "   chL: "<< chL[iBar] << "    chR: " <<chR[iBar] <<std::endl;
  }

  //--- define branches
  float step1, step2;
  int channelIdx[256];
  std::vector<float> *tot = 0;
  std::vector<float> *energy = 0;
  std::vector<long long> *time = 0;
  int nhits;
  float x, y;

  tree -> SetBranchStatus("*",0);
  tree -> SetBranchStatus("step1",  1); tree -> SetBranchAddress("step1",  &step1);
  tree -> SetBranchStatus("step2",  1); tree -> SetBranchAddress("step2",  &step2);

  tree -> SetBranchStatus("channelIdx",  1); tree -> SetBranchAddress("channelIdx",  channelIdx);

  tree -> SetBranchStatus("tot",    1); tree -> SetBranchAddress("tot",       &tot);
  tree -> SetBranchStatus("energy", 1); tree -> SetBranchAddress("energy", &energy);
  tree -> SetBranchStatus("time",   1); tree -> SetBranchAddress("time",     &time);
  
  
  tree -> SetBranchStatus("nplanes", 1);   tree -> SetBranchAddress("nplanes",  &nhits);
  tree -> SetBranchStatus("x_dut", 1);     tree -> SetBranchAddress("x_dut",        &x);
  tree -> SetBranchStatus("y_dut", 1);     tree -> SetBranchAddress("y_dut",        &y);
 

  //--- get plot settings
  std::vector<float> Vov = opts.GetOpt<std::vector<float> >("Plots.Vov");
  std::vector<int> energyBins = opts.GetOpt<std::vector<int> >("Plots.energyBins");
  std::vector<int> energyMins = opts.GetOpt<std::vector<int> >("Plots.energyMins");
  std::vector<int> energyMaxs = opts.GetOpt<std::vector<int> >("Plots.energyMaxs");

  std::map<float,int> map_energyBins;
  std::map<float,int> map_energyMins;
  std::map<float,int> map_energyMaxs;
  for(unsigned int ii = 0; ii < Vov.size(); ++ii)
    {
      map_energyBins[Vov[ii]] = energyBins[ii];
      map_energyMins[Vov[ii]] = energyMins[ii];
      map_energyMaxs[Vov[ii]] = energyMaxs[ii];
    }



  // -- read minimum energy for each bar from file
  float Xmin = opts.GetOpt<float>("Cuts.Xmin");
  float Xmax = opts.GetOpt<float>("Cuts.Xmax");

  int vetoOtherBars = opts.GetOpt<int>("Cuts.vetoOtherBars");
  std::string minEnergiesFileName = opts.GetOpt<std::string>("Cuts.minEnergiesFileName");
  std::map < std::pair<int, float>, float> minE;
  if (minEnergiesFileName != "") {
    std::ifstream minEnergiesFile;
    minEnergiesFile.open(minEnergiesFileName);
    std::string line;
    int bar;
    float ov;
    float value;
    while ( minEnergiesFile.good() ){
      getline(minEnergiesFile, line);
      std::istringstream ss(line);
      ss >> bar >> ov >> value;
      minE[std::make_pair(bar,ov)] = value;
      //std::cout<< bar <<  "   " << ov << "  " << minE[std::make_pair(bar,ov)] <<std::endl;
    }
  }
  else{
    for(unsigned int iBar = 0; iBar < channelMapping.size()/2; ++iBar){
      for(unsigned int ii = 0; ii < Vov.size(); ++ii){
        minE[std::make_pair(iBar, Vov[ii])] = map_energyMins[Vov[ii]];
      }
    }
  }



  //--- define output files and  histograms
  std::string outFileName = opts.GetOpt<std::string>("Output.outFileName");
  TFile* outFile = TFile::Open(Form("%s",outFileName.c_str()),"RECREATE");
  std::cout << "Output file name : " << outFile->GetName() <<std::endl;
  outFile -> cd();
  TH2F *h2_beamXY = new TH2F("h2_beamXY","h2_beamXY",300,-30.,30., 300, -30., -30.);
  std::map<int,TH1F*> h1_energyLR;
  std::map<int,TH1F*> h1_energyLR_ext;

  std::map<int,TH1F*> h1_N_vs_Y;
  std::map<int,TH2F*> h2_N_vs_XY;

  std::map<int,TH1F*> h1_N_vs_Y_energySel;
  std::map<int,TH2F*> h2_N_vs_XY_energySel;

  std::map<int,TH1F*> h1_eff_vs_Y;
  std::map<int,TH2F*> h2_eff_vs_XY;

  std::map<int,TProfile*> p1_eff_vs_Y;
  std::map<int,TProfile2D*> p2_eff_vs_XY;

  std::map<int,TProfile2D*> p2_eff_vs_XY_ext;
  std::map<int,TProfile*> p1_eff_vs_X_ext;

  std::map<int,std::vector<float>*> ranges1;
  std::map<int,std::vector<float>*> ranges;
  std::map<int,bool> hasTrack;
  std::map<int,bool> hasMIPInRefModule;
  std::map<int,bool> isShoweringEvent;

  // -- Coincidence pre loop   
  if( !opts.GetOpt<std::string>("Coincidence.status").compare("yes") ){
    
    float energyL_ext;
    float energyR_ext;
    int chL_ext = opts.GetOpt<float>("Coincidence.chL");//NB: gli passo direttamente da cfg il ch barra 8 +64
    int chR_ext = opts.GetOpt<float>("Coincidence.chR");//NB: gli passo direttamente da cfg il ch barra 8 +64
    
    int nEntries = tree->GetEntries();
    if( maxEntries > 0 ) nEntries = maxEntries;
    for(int entry = 0; entry < nEntries; ++entry){
      
      tree -> GetEntry(entry);
      
      if( entry%500000 == 0 ){
	std::cout << ">>> External bar loop: reading entry " << entry << " / " << nEntries << " (" << 100.*entry/nEntries << "%)" << std::endl;
      }
      
      hasTrack[entry] = false;
      hasMIPInRefModule[entry] = false;
      isShoweringEvent[entry] = false;

      // -- skip events without track info
      if ( nhits <=0 ||  nhits>12 || x < -100 || y < -100 ) {
	continue;
      }
	
      hasTrack[entry] = true;

      h2_beamXY ->Fill(x,y);


      float Vov = step1;
      float vth1 = float(int(step2/10000)-1);
      float vth2 = float(int((step2-10000*(vth1+1))/100.)-1);
      float vth = 0.;
      if(!opts.GetOpt<std::string>("Input.vth").compare("vth1"))  { vth = vth1;}
      if(!opts.GetOpt<std::string>("Input.vth").compare("vth2"))  { vth = vth2;}
            
      // --- count active bars in the module, to remove showering events
      int   nActiveBarsArray = 0;
      for(int iBar = 0; iBar < int(channelMapping.size())/2; ++iBar) {
	int chL_iext = channelMapping[iBar*2+0];// array0 for coincidence is hard coded... - to be fixed
	int chR_iext = channelMapping[iBar*2+1];// array0 for coincidence is hard coded... - to be fixed
	//int chL_iext = channelMapping[iBar*2+0]+64;// array1 for coincidence is hard coded... - to be fixed
	//int chR_iext = channelMapping[iBar*2+1]+64;// array1 for coincidence is hard coded... - to be fixed
	float energyL_iext = (*energy)[channelIdx[chL_iext]];
	float energyR_iext = (*energy)[channelIdx[chR_iext]];
	float totL_iext    = 0.001*(*tot)[channelIdx[chL_iext]];
	float totR_iext    = 0.001*(*tot)[channelIdx[chR_iext]];
	if ( totL_iext > -10 && totL_iext < 100 && totR_iext > -10 && totR_iext < 100   ){
	  float energyMean=(energyL_iext+energyR_iext)/2;
	  if (energyMean>0){
	    nActiveBarsArray+=1;
	  }
	}
      }
      if (vetoOtherBars && nActiveBarsArray > 3 ) {
	isShoweringEvent[entry] = true;
	continue;
      }
            
      if (channelIdx[chL_ext] <0 || channelIdx[chR_ext] <0) continue;
      energyL_ext = (*energy)[channelIdx[chL_ext]];
      energyR_ext = (*energy)[channelIdx[chR_ext]];
      
      //--- create histograms, if needed
      int index( (10000*int(Vov*100.)) + (100*vth) + 99 );
      if( h1_energyLR_ext[index] == NULL ){
	h1_energyLR_ext[index] = new TH1F(Form("h1_energy_external_barL-R_Vov%.2f_th%02.0f",Vov,vth),"",map_energyBins[Vov],map_energyMins[Vov],map_energyMaxs[Vov]);
      }
      
      h1_energyLR_ext[index] -> Fill(0.5*(energyL_ext + energyR_ext));	
    
    }// -- end loop over entries (coincidence pre-loop)
    
    

    // -- find min energy for coincidence bar
    for( auto index : h1_energyLR_ext){
      ranges1[index.first] = new std::vector<float>;
      
      float Vov = float ((int(index.first /10000))/100.);
      float vth1 = float(int((index.first-Vov*10000*100)/100.));
      float vth2 = float(int((step2-10000*(vth1+1))/100.)-1);
      
      if( opts.GetOpt<int>("Channels.array") == 0){
	index.second->GetXaxis()->SetRangeUser(50,900);
      }
      if( opts.GetOpt<int>("Channels.array") == 1){
	index.second->GetXaxis()->SetRangeUser(50,900);
      }
      
      float max = index.second->GetBinCenter(index.second->GetMaximumBin());
      index.second->GetXaxis()->SetRangeUser(0,1024);
      
      TF1* f_pre = new TF1(Form("fit_energy_coincBar_Vov%.2f_vth1_%02.0f",Vov,vth1), "[0]*TMath::Landau(x,[1],[2])", 0, 1000.);
      f_pre -> SetRange(max*0.70, max*1.5);
      f_pre -> SetLineColor(kBlack);
      f_pre -> SetLineWidth(2);
      f_pre -> SetParameters(index.second->Integral(index.second->GetMaximumBin(), index.second->GetNbinsX())/10, max, 0.1*max);
      f_pre -> SetParLimits(1, 0, 9999);
      f_pre -> SetParLimits(2, 0, 9999);
      index.second->Fit(f_pre, "QRS+");
      
      if (f_pre->GetParameter(1)>20)
	ranges1[index.first] -> push_back( 0.70*f_pre->GetParameter(1));
      else
	ranges1[index.first] -> push_back( 20 );
      
      ranges1[index.first] -> push_back( 950 );
      
      std::cout << "Vov = " << Vov << "  vth1 = " << vth1 << "   vth2 = " << vth2
		<< "    Coincidence bar - energy range:  " << ranges1[index.first]->at(0) << " - " << ranges1[index.first]->at(1)<< std::endl;
    }
  }
  

  
  //------------------------
  //--- 1st loop over events
  int nEntries = tree->GetEntries();
  if( maxEntries > 0 ) nEntries = maxEntries;
  for(int entry = 0; entry < nEntries; ++entry)
    {
      tree -> GetEntry(entry);
      if( entry%500000 == 0 )
	{
	  std::cout << ">>> 1st loop: reading entry " << entry << " / " << nEntries << " (" << 100.*entry/nEntries << "%)" << std::endl;
	}
      
      
      if(!hasTrack[entry] ) continue;
      if(isShoweringEvent[entry] ) continue;
      
	
      float Vov = step1;
      float vth1 = float(int(step2/10000)-1);
      float vth2 = int((step2-10000*(vth1+1))/100.)-1;
      float vth = 0;
      std::string vthMode = opts.GetOpt<std::string>("Input.vth");
      if(!opts.GetOpt<std::string>("Input.vth").compare("vth1"))  { vth = vth1;}
      if(!opts.GetOpt<std::string>("Input.vth").compare("vth2"))  { vth = vth2;}
      
      
      // -- remove showering events
      int   nActiveBarsArray = 0;
      for(unsigned int iBar = 0; iBar < channelMapping.size()/2; ++iBar)
	{
	  float avEn = 0.5 * ( (*energy)[channelIdx[chL[iBar]]] + (*energy)[channelIdx[chR[iBar]]] );
	  if (avEn > 0) nActiveBarsArray+=1;
	}
      
      if ( vetoOtherBars && nActiveBarsArray > 3 ) {
	isShoweringEvent[entry] = true;
	continue; 
      }




      // --- check coincidence with another channel
      if(!opts.GetOpt<std::string>("Coincidence.status").compare("yes"))
	{
	  
	  int label = (10000*int(Vov*100.)) + (100*vth) + 99;
	  
	  if ( p2_eff_vs_XY_ext[label] == NULL ){
	    p2_eff_vs_XY_ext[label] = new TProfile2D(Form("p2_eff_vs_XY_refBar_Vov%.2f_th%02.0f",Vov,vth),"", 300, -30,30, 300, -30, 30);
	    p1_eff_vs_X_ext[label]  = new TProfile(Form("p1_eff_vs_X_refBar_Vov%.2f_th%02.0f",Vov,vth),"", 300, -30,30);
	  }
	  
	  int chL_ext = opts.GetOpt<int>("Coincidence.chL");
	  int chR_ext = opts.GetOpt<int>("Coincidence.chR");
	  float avEn = 0;
	  if (channelIdx[chL_ext] >= 0 &&  channelIdx[chR_ext] >= 0) {
	    float energyL_ext = (*energy)[channelIdx[chL_ext]];
	    float energyR_ext = (*energy)[channelIdx[chR_ext]];
	    avEn = 0.5 * ( energyL_ext + energyR_ext);
	  }

	  int weight =  avEn > ranges1[label]-> at(0);
	  p2_eff_vs_XY_ext[label] -> Fill(x,y,weight);
	  p1_eff_vs_X_ext[label]  -> Fill(x,weight);
	  
	  if (  avEn >= ranges1[label]-> at(0) )  {
	    hasMIPInRefModule[entry] = true;
	  }
	  else {
	    hasMIPInRefModule[entry] = false;
	    continue;
	  }
	  
	  
	}// -- coincidence
	
	
      
      // -- fill energy histograms
      for(unsigned int iBar = 0; iBar < channelMapping.size()/2; ++iBar)
	{
	  //--- create histograms, if needed
	  int index( (10000*int(Vov*100.)) + (100*vth) + iBar );
	  if( h1_energyLR[index] == NULL )
	    {
	      h1_energyLR[index] = new TH1F(Form("h1_energy_bar%02dL-R_Vov%.2f_th%02.0f",iBar,Vov,vth),"",map_energyBins[Vov],map_energyMins[Vov],map_energyMaxs[Vov]);
	    }
	  
	  //--- fill energy histogram for good events (good = not crazy values of ToT)
	  float totL = 0.001*(*tot)[channelIdx[chL[iBar]]];
	  float totR = 0.001*(*tot)[channelIdx[chR[iBar]]];
	  if (totL>-10 && totR>-10 && totL<100 && totR<100) 
	    {
	      h1_energyLR[index] ->Fill( 0.5 * ( (*energy)[channelIdx[chL[iBar]]] + (*energy)[channelIdx[chR[iBar]]]  ) );
	    }
	}
      
    } // end loop over entries


  
    // --- fit energy histograms
    TH1F* histo;
    std::map<int,TF1*>  f_landau; // f_gaus[index]        

    for( auto it : h1_energyLR){
      
      int index = it.first;
      histo = it.second;
      
      ranges[index] = new std::vector<float>;

      float Vov = float ((int(index /10000))/100.);
      float vth1 = float(int((index-Vov*10000*100)/100.));
      int iBar = index  - (10000*int(Vov*100.)) - (100*vth1);

     
      if( opts.GetOpt<int>("Channels.array") == 1){
	histo->GetXaxis()->SetRangeUser(minE[std::make_pair(iBar, Vov)], 950);
      }
      if( opts.GetOpt<int>("Channels.array") == 0){
	histo->GetXaxis()->SetRangeUser(minE[std::make_pair(iBar, Vov)], 950);
      }
      float max = histo->GetBinCenter(histo->GetMaximumBin());
      histo->GetXaxis()->SetRangeUser(0,1024);

      f_landau[index] = new TF1(Form("f_landau_bar%02dLR_Vov%.2f_vth1_%02.0f", iBar,Vov,vth1),"[0]*TMath::Landau(x,[1],[2])", 0,1000.);
      float xmin = max * 0.65;
      float xmax = std::min(max*2.5, 950.);
      f_landau[index] -> SetRange(xmin,xmax);
      f_landau[index] -> SetParameters(histo->Integral(histo->GetMaximumBin(), histo->GetNbinsX())/10, max, 0.1*max);
      f_landau[index] -> SetParLimits(1,0,9999);
      f_landau[index] -> SetParLimits(2,0,9999);
      histo -> Fit(f_landau[index],"QRS");
      if ( f_landau[index]->GetParameter(1) > 0 ){
	xmin = f_landau[index]->GetParameter(1) - 3 * std::abs(f_landau[index]->GetParameter(2));
	if (xmin < minE[std::make_pair(iBar, Vov)]) { xmin = minE[std::make_pair(iBar, Vov)]; } 
	xmax = std::min(f_landau[index]->GetParameter(1) * 2.5, 950.);
	f_landau[index] -> SetRange(xmin, xmax);
	f_landau[index] -> SetParameters(histo->Integral(histo->GetMaximumBin(), histo->GetNbinsX())/10, f_landau[index]->GetParameter(1), 0.1*f_landau[index]->GetParameter(1));
      }
      histo -> Fit(f_landau[index],"QRS");

      if ( f_landau[index]->GetNDF() > 0 && f_landau[index]->GetParameter(1) > minE[std::make_pair(iBar, Vov)] &&
	   (f_landau[index]->GetParameter(1) - 3.0 * std::abs(f_landau[index]->GetParameter(2))) >=  minE[std::make_pair(iBar, Vov)] &&
	   (f_landau[index]->GetParameter(1) - 3.0 * std::abs(f_landau[index]->GetParameter(2))) < 950) {
	ranges[index] -> push_back( f_landau[index]->GetParameter(1) - 3.0 * std::abs(f_landau[index]->GetParameter(2)));
      }
      else
	ranges[index] -> push_back( minE[std::make_pair(iBar, Vov)] ); //   
      
      ranges[index] -> push_back( 950 );
      
      
    }
    

    



    // --- Second loop over entries to compute efficiency
    for(int entry = 0; entry < nEntries; ++entry)
      {
        tree -> GetEntry(entry);
        if( entry%500000 == 0 )
          {
	    std::cout << ">>> 2nd loop: reading entry " << entry << " / " << nEntries << " (" << 100.*entry/nEntries << "%)" << std::endl;
          }
	


	// this selection defines the denominator
	if ( isShoweringEvent[entry] ) continue;
	//if ( !hasTrack[entry] ) continue;
	//if (!hasTrack[entry] || !hasMIPInRefModule[entry])  continue;
	if (!hasTrack[entry] || !hasMIPInRefModule[entry] ||  x < Xmin || x > Xmax) continue;


        float Vov = step1;
        float vth = float(int(step2/10000)-1);

	// -- fill histograms for each bar
	for(unsigned int iBar = 0; iBar < channelMapping.size()/2; ++iBar)
	  {
	    int index( (10000*int(Vov*100.)) + (100*vth) + iBar );
	    
	    //--- create histograms, if needed
	    if(h1_N_vs_Y[index] == NULL )
	      {
		h1_N_vs_Y[index]  = new TH1F(Form("h1_N_vs_Y_bar%02d_Vov%.2f_th%02.0f",iBar,Vov,vth),"", 300, -30,30);
		h2_N_vs_XY[index] = new TH2F(Form("h2_N_vs_XY_bar%02d_Vov%.2f_th%02.0f",iBar,Vov,vth),"", 300, -30,30, 300, -30, 30);
		h1_N_vs_Y_energySel[index]  = new TH1F(Form("h1_N_vs_Y_energySel_bar%02d_Vov%.2f_th%02.0f",iBar,Vov,vth),"", 300, -30,30);
		h2_N_vs_XY_energySel[index] = new TH2F(Form("h2_N_vs_XY_energySel_bar%02d_Vov%.2f_th%02.0f",iBar,Vov,vth),"", 300, -30,30, 300, -30, 30);
		p1_eff_vs_Y[index] = new TProfile(Form("p1_eff_vs_Y_bar%02d_Vov%.2f_th%02.0f",iBar,Vov,vth),"", 300, -30,30);
		p2_eff_vs_XY[index] = new TProfile2D(Form("p2_eff_vs_XY_bar%02d_Vov%.2f_th%02.0f",iBar,Vov,vth),"", 300, -30,30, 300, -30, 30);
	      }
	    
	    
	    float energyLR = 0;
	    if (channelIdx[chL[iBar]] >=0 && channelIdx[chR[iBar]] >=0){
	      energyLR = 0.5*( (*energy)[channelIdx[chL[iBar]]] + (*energy)[channelIdx[chR[iBar]]]  );
	    }

	   	    
	    //--- fill histograms
	    h1_N_vs_Y[index] -> Fill( y );
	    h2_N_vs_XY[index] -> Fill( x, y );
	      
	    if (energyLR > ranges[index]->at(0)){
	      h1_N_vs_Y_energySel[index] -> Fill( y );
	      h2_N_vs_XY_energySel[index] -> Fill( x, y );
	    } 
	    
	    int weight = ( energyLR > ranges[index]->at(0) );
	    p1_eff_vs_Y[index] -> Fill( y, weight );
	    p2_eff_vs_XY[index] -> Fill( x, y, weight );
	    
	  }
      
      }
    
    for( auto it : h1_N_vs_Y_energySel){
      int index = it.first;

      float Vov = float ((int(index /10000))/100.);
      float vth1 = float(int((index-Vov*10000*100)/100.));
      int iBar = index  - (10000*int(Vov*100.)) - (100*vth1);

      h1_eff_vs_Y[index] = (TH1F*)h1_N_vs_Y_energySel[index]->Clone();
      h1_eff_vs_Y[index]->SetName(Form("h1_eff_vs_Y_bar%02d_Vov%.2f_th%02d", iBar,Vov,int(vth1)));
      h1_eff_vs_Y[index]->SetTitle(Form("h1_eff_vs_Y_bar%02d_Vov%.2f_th%02d", iBar,Vov,int(vth1)));
      h1_eff_vs_Y[index]->Divide(h1_N_vs_Y[index]);
      
      h2_eff_vs_XY[index] = (TH2F*)h2_N_vs_XY_energySel[index]->Clone();
      h2_eff_vs_XY[index]->SetName(Form("h2_eff_vs_XY_bar%02d_Vov%.2f_th%02d", iBar,Vov,int(vth1)));
      h2_eff_vs_XY[index]->SetTitle(Form("h2_eff_vs_XY_bar%02d_Vov%.2f_th%02d", iBar,Vov,int(vth1)));
      h2_eff_vs_XY[index]->Divide(h2_N_vs_XY[index]);
    }


    // -- fit efficiency vs position  - ref module
    TProfile* prof;
    std::map<int,TF1*>  fitEff;
    for (auto it : p1_eff_vs_X_ext){
      
      int label = it.first;
      prof = it.second;
      
      float Vov = (int(label/10000))/100.;
      float vth1 = label - 99 - (10000*int(Vov*100.))/100.;
      
      fitEff[label] = new TF1(Form("fitEff_barRef_Vov%.2f_th%02d", Vov,int(vth1)),fitEfficiencyVsPosition, -20., 20., 5); 
      fitEff[label]->SetNpx(5000);
      int binmax = prof->GetMaximumBin(); 
      float x0 = prof->GetBinCenter(binmax);
      x0 = (Xmin+Xmax)/2;
      fitEff[label]->SetParameter(0, x0);  // center
      fitEff[label]->SetParameter(1, 3.);  // crystal width
      fitEff[label]->SetParameter(2, 0.1); // baseline
      fitEff[label]->SetParameter(3, 0.7); // max eff
      fitEff[label]->SetParameter(4, 0.4); // sigma
      fitEff[label]->SetParLimits(0, x0-10, x0+10);
      fitEff[label]->SetParLimits(1, 3.0, 3.4);
      fitEff[label]->SetParLimits(2, 0.0, 0.2);
      fitEff[label]->SetParLimits(3, 0.5, 1.0);
      fitEff[label]->SetParLimits(4, 0.1, 1.0);
      fitEff[label]->SetRange(x0-5, x0+5);
      p1_eff_vs_X_ext[label]  ->  Fit(fitEff[label],"QRS+");
    }
    

    // -- fit efficiency vs position  - test module
    for( auto it : p1_eff_vs_Y){
      int index = it.first;
      prof = it.second;
      
      float Vov = float ((int(index /10000))/100.);
      float vth1 = float(int((index-Vov*10000*100)/100.));
      int iBar = index  - (10000*int(Vov*100.)) - (100*vth1);

      prof->SetMarkerColor(51+iBar*4);
      prof->SetLineColor(51+iBar*4);
            
      fitEff[index] = new TF1(Form("fitEff_bar%02d_Vov%.2f_th%02d", iBar,Vov,int(vth1)),fitEfficiencyVsPosition, -20., 20., 5); 
      fitEff[index]->SetNpx(5000);
      fitEff[index]->SetLineColor(51+iBar*4);
      prof-> GetXaxis()->SetRangeUser(-17.,17.);
      int binmax = prof->GetMaximumBin(); 
      float x0 = prof->GetBinCenter(binmax);
      fitEff[index]->SetParameter(0, x0);  // center
      fitEff[index]->SetParameter(1, 3.);  // crystal width
      fitEff[index]->SetParameter(2, 0.1); // baseline
      fitEff[index]->SetParameter(3, 0.7); // max eff
      fitEff[index]->SetParameter(4, 0.4); // sigma
      fitEff[index]->SetParLimits(0, x0-10, x0+10);
      fitEff[index]->SetParLimits(1, 3.0, 3.4);
      fitEff[index]->SetParLimits(2, 0.0, 0.2);
      fitEff[index]->SetParLimits(3, 0.5, 1.0);
      fitEff[index]->SetParLimits(4, 0.1, 1.0);
      fitEff[index]->SetRange(x0-5, x0+5);
      prof-> GetXaxis()->SetRangeUser(-30,30);
      prof->Fit(fitEff[index],"QRS+");
    }


    
    std::cout << std::endl;
    outFile -> Write();
 
}
