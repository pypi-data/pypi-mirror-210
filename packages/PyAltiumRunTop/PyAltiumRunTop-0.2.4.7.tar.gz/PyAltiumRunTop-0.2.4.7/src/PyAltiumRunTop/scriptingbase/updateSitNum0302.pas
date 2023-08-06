{..............................................................................}

{..............................................................................}
//
Procedure UpDateSiteNum(Var fileName: string);
Var
  CurrentSch: ISch_Sheet;
  Iterator: ISch_Iterator;
  PIterator: ISch_Iterator;
  AComponent: ISch_Component;
  AnIndex: Integer;
  Model: ISch_Implementation;
  // FileName    : TDynamicString;
//  ReportList: TStringList;
  Parameter: ISch_Parameter;
  Document: IServerDocument;

  FlagStr: String;
  ObjectList: TStringList;
  RptFile: TextFile;
  LS: String;
  I: Integer;
  G: Integer;
  G1: Integer;
  Splitted: TStringList;
  NameList: TStringList;
  currentTime: TDataTime;
  Splitted1: TStringList;
  Sdy   : TDynamicString;
Begin
  // Check if schematic server exists or not.
  If SchServer = Nil Then Exit;

  // Obtain the current schematic document interface.
  CurrentSch := SchServer.GetCurrentSchDocument;
  If CurrentSch = Nil Then Exit;
  ObjectList := TStringList.Create;
  NameList := TStringList.Create;
  NameList.Add('componentCoding');
  NameList.Add('componentDesc');
  NameList.Add('manufacturerCode');
  NameList.Add('manufacturerName');
  NameList.Add('materialGroupDesc');
  NameList.Add('materialInTheClassDesc');
  // FileName := ;
  //fileName
  AssignFile(RptFile, 'D:\adTemp\' + fileName);
  Reset(RptFile);
  while not Eof(RptFile) do
  begin
    Readln(RptFile, LS);
    if (LS <> NULL) then
      ObjectList.Add(LS);
    //ShowMessage(Ls);
  end;
  CloseFile(RptFile);

  // Look for components only
  Iterator := CurrentSch.SchIterator_Create;
  Iterator.AddFilter_ObjectSet(MkSet(eSchComponent));


//  ReportList := TStringList.Create;
  Try
    AComponent := Iterator.FirstSchObject;
    While AComponent <> Nil Do
    Begin
      //ReportList.Add(AComponent.Designator.Name + ' ' + AComponent.Designator.Text);
      //ReportList.Add(' Pins');
      FlagStr := 'F';
      Sdy := '';
      for I := 0 to ObjectList.Count - 1 do
      begin
        if StartsText(AComponent.Designator.Text + '!!!!!', ObjectList[I]) then
        begin
//          ShowMessage(ObjectList[I]);
          FlagStr := 'T';
          currentTime := Now;
          Splitted1 := TStringList.Create;
          Splitted1.LineBreak := '!!!!!';
          Splitted1.Text := ObjectList[I];
//      Model := AComponent.AddPart;
          for G1 := 0 to Splitted1.Count - 1 do
          begin
            if G1 = 0 Then
            begin
              Sdy := Sdy+ 'Designator:'+Splitted1[G1]+' ';
            end;
            if G1 = 1 Then
            begin
               Sdy := Sdy+ 'componentCoding:'+Splitted1[G1]+',';
//              Parameter.Name := 'componentCoding';
            end;
            if G1 = 2 Then
            begin
//              Parameter.Name := 'componentDesc';
               Sdy := Sdy+ 'componentDesc:'+Splitted1[G1]+',';
            end;
            if G1 = 3 Then
            begin
//              Parameter.Name := 'manufacturerCode';
               Sdy := Sdy+ 'manufacturerCode:'+Splitted1[G1]+',';
            end;
            if G1 = 4 Then
            begin
//              Parameter.Name := 'manufacturerName';
               Sdy := Sdy+ 'manufacturerName:'+Splitted1[G1]+',';
            end;
            if G1 = 5 Then
            begin
//              Parameter.Name := 'materialGroupDesc';
               Sdy := Sdy+ 'materialGroupDesc:'+Splitted1[G1]+',';
            end;
            if G1 = 6 Then
            begin
//              Parameter.Name := 'materialInTheClassDesc';
               Sdy := Sdy+ 'materialInTheClassDesc:'+Splitted1[G1]+',';
            end;
          end;

          log_str('Same Designator Text:' + Sdy);
          Splitted1.Free;
          break;
        end;
      end;
      if 'T' <> FlagStr then
      begin
        AComponent := Iterator.NextSchObject;
        Continue;
      end;


      Try
        PIterator := AComponent.SchIterator_Create;
        PIterator.AddFilter_ObjectSet(MkSet(eParameter));

        Parameter := PIterator.FirstSchObject;

        While Parameter <> Nil Do
        Begin
          // ShowMessage(Parameter.Name);
          if NameList.IndexOf(Parameter.Name) >= 0 then
          begin
            AComponent.RemoveSchObject(Parameter);
          end;

//             ReportList.Add('  Parameter.Text: ' + Parameter.Text  );
//             ReportList.Add('  Parameter.Name: ' + Parameter.Name  );
//             ReportList.Add('  Name: ' + Parameter.Name + ' Designator: ' + Parameter.Designator );
//             ReportList.Add( ' Orientation: ' +  OrientationToStr(Parameter.Designator));
          Parameter := PIterator.NextSchObject;
        End;
      Finally
        AComponent.SchIterator_Destroy(PIterator);
      End;


      Splitted := TStringList.Create;
      Splitted.LineBreak := '!!!!!';
      Splitted.Text := ObjectList[I];
//      Model := AComponent.AddPart;
      for G := 1 to Splitted.Count - 1 do
      begin
        // ShowMessage(G);
        Parameter := SchServer.SchObjectFactory(eParameter, eCreate_Default);
        Parameter.IsHidden := True;
        if G = 1 Then
        begin
          Parameter.Name := 'componentCoding';
        end;
        if G = 2 Then
        begin
          Parameter.Name := 'componentDesc';
        end;
        if G = 3 Then
        begin
          Parameter.Name := 'manufacturerCode';
        end;
        if G = 4 Then
        begin
          Parameter.Name := 'manufacturerName';
        end;
        if G = 5 Then
        begin
          Parameter.Name := 'materialGroupDesc';
        end;
        if G = 6 Then
        begin
          Parameter.Name := 'materialInTheClassDesc';
        end;
        Parameter.Text := Splitted[G];
        Parameter.ParamType := eParameterType_String;
        Parameter.ReadOnlyState := eReadOnly_None;
        AComponent.AddSchObject(Parameter);
      end;
      Splitted.Free;
//      Model.IsCurrent := True;
//      Model.UseComponentLibrary := False;  //Refer to the WTH of the Location section of Sim Editor dialog.
      //  Model := AComponent.AddSchImplementation;
      // Parameter := SchServer.SchObjectFactory(eParameter, eCreate_Default);

      // Parameter.Name := 'materialInTheClassDesc';

      // Parameter.Text := Splitted[G];
      // Parameter.ParamType := eParameterType_String;
      // Parameter.ReadOnlyState := eReadOnly_None;
      // Model.AddSchObject(Parameter);


//      ReportList.Add('');
      AComponent := Iterator.NextSchObject;
    End;
  Finally
    CurrentSch.SchIterator_Destroy(Iterator);
  End;

  // ReportList.SaveToFile('D:\PinReport4.Txt');
  ObjectList.Free;
  ShowMessage('Finished !!!');
  // Display the report for all components found and their associated pins.
  // Document := Client.OpenDocument('Text','D:\PinReport4.txt');
  // If Document <> Nil Then
  //  Client.ShowDocument(Document);
End;
{..............................................................................}

{..............................................................................}
End.
