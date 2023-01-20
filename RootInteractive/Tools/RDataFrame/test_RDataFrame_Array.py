# from RootInteractive.Tools.RDataFrame.RDataFrame_Array  import *

import ROOT
import ast
import RDataFrame_Array

import pprint
def makeTestRDataFrame():
    # 2 hacks - instatiate classes needed for RDataframe
    x=ROOT.AliExternalTrackParam();
    ROOT.gInterpreter.ProcessLine(".L $NOTES/JIRA/ATO-615/statCounters.C+g")

    ROOT.gInterpreter.Declare("""
        #pragma link C++ class ROOT::RVec < ROOT::RVec < float>> + ;
        auto makeUnitRVec1D = [](int n){
            auto array = ROOT::RVecF(n);
            array.resize(n);
            for (size_t i=0; i<n; i++) array[i]=i;
            return array;
        ;};
        auto makeUnitRVec2D = [](int n1, int n2){
            auto array2D = ROOT::RVec<ROOT::RVec<float>>(n1);
            array2D.resize(n2);
            for (size_t i=0; i<n1; i++) {
                array2D[i].resize(n2);
                for (size_t j=0; j<n2; j++) array2D[i][j]=i+j;
                }
            return array2D;
        ;};
        auto makeUnitRVec1DTrack = [](int n){
            auto array = ROOT::RVec<AliExternalTrackParam>(n);
            array.resize(n);
            //for (size_t i=0; i<n; i++) array=i;
            return array;
        ;};
    """)
    #
    nTracks=100
    df= ROOT.RDataFrame(nTracks);
    rdf=df.Define("nPoints", "int(40 + gRandom->Rndm() * 200)")
    rdf=rdf.Define("nPoints2", "int(40 + gRandom->Rndm() * 200)")
    #rdf= rdf.Define('array', 'ROOT::RVecF(mean)')
    rdf= rdf.Define("array1D0","makeUnitRVec1D(nPoints)")
    rdf= rdf.Define("array1D2","makeUnitRVec1D(nPoints)")
    rdf= rdf.Define("array2D0","makeUnitRVec2D(nPoints,nPoints2)")
    rdf= rdf.Define("array2D1","makeUnitRVec2D(nPoints,nPoints2)")
    #rdf= rdf.Define('array1DTrack',"makeUnitRVec1DTrack(nPoints)")
    rdf.Snapshot("makeTestRDataFrame","makeTestRDataFrame.root")
    return rdf

def generateASTExample():
    astOut=ast.parse("track.GetP() / mass", mode="eval")
    ast.dump(astOut,True,False)
def dumpAST(expression):
    astOut=ast.parse(expression, mode="eval")
    print(ast.dump(astOut,True,False))


def define1D(rdf, name, expression,verbosity):
    """
    :param rdf:
    :param expression:
    :return:
    1.) make AST
    2.) check get data
    expression="array1D0[:]+array1D1[:]"
    expression="array1D0[0:10]+array1D1[10:20]"
    expression="array1D0[0:10]+array1D1[0]"
    expression="cos(array1D0[0:10]+array1D1[0:10])"
    expression="array1D0[0:10].fun(0)"
    """
    astOut=ast.parse(expression, mode="eval")
    print(ast.dump(astOut,True,False))
    # to get type
    columnTypes={}             # id-> types
    validExpression={}         # to check ROOT.expr
    typeDim={}                 # type dimension   stl::vector<>   ROOT::RVec<>
    # make function header  ->  auto name(columns)
    # loop over id='array1D0
    rdf.GetColumnType("array1D0")
    #
    #rdfNew=rdf
    return rdf

def define2D(rdf, expression):
    rdfNew=rdf
    return rdf
