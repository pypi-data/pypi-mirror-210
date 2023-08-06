
--  This package provides contants to refer to Librflxlang types and struct
--  members in the generic introspection API
--  (``Langkit_Support.Generic_API.Introspection``).

with Langkit_Support.Generic_API.Introspection;

package Librflxlang.Generic_API.Introspection is

   package G renames Langkit_Support.Generic_API.Introspection;

   ---------------------
   -- Type references --
   ---------------------

   package Type_Refs is
         Analysis_Unit : constant G.Type_Ref :=
           G.From_Index (Self_Id, 1);
         Big_Integer : constant G.Type_Ref :=
           G.From_Index (Self_Id, 2);
         Boolean : constant G.Type_Ref :=
           G.From_Index (Self_Id, 3);
         Character_Type : constant G.Type_Ref :=
           G.From_Index (Self_Id, 4);
         Integer : constant G.Type_Ref :=
           G.From_Index (Self_Id, 5);
         Source_Location_Range : constant G.Type_Ref :=
           G.From_Index (Self_Id, 6);
         Text_Type : constant G.Type_Ref :=
           G.From_Index (Self_Id, 7);
         Token_Reference : constant G.Type_Ref :=
           G.From_Index (Self_Id, 8);
         Unbounded_Text_Type : constant G.Type_Ref :=
           G.From_Index (Self_Id, 9);
         Analysis_Unit_Kind : constant G.Type_Ref :=
           G.From_Index (Self_Id, 10);
         Lookup_Kind : constant G.Type_Ref :=
           G.From_Index (Self_Id, 11);
         Designated_Env_Kind : constant G.Type_Ref :=
           G.From_Index (Self_Id, 12);
         Grammar_Rule : constant G.Type_Ref :=
           G.From_Index (Self_Id, 13);
         R_F_L_X_Node_Array : constant G.Type_Ref :=
           G.From_Index (Self_Id, 14);
         R_F_L_X_Node : constant G.Type_Ref :=
           G.From_Index (Self_Id, 15);
         Abstract_I_D : constant G.Type_Ref :=
           G.From_Index (Self_Id, 16);
         I_D : constant G.Type_Ref :=
           G.From_Index (Self_Id, 17);
         Unqualified_I_D : constant G.Type_Ref :=
           G.From_Index (Self_Id, 18);
         Aspect : constant G.Type_Ref :=
           G.From_Index (Self_Id, 19);
         Attr : constant G.Type_Ref :=
           G.From_Index (Self_Id, 20);
         Attr_First : constant G.Type_Ref :=
           G.From_Index (Self_Id, 21);
         Attr_Has_Data : constant G.Type_Ref :=
           G.From_Index (Self_Id, 22);
         Attr_Head : constant G.Type_Ref :=
           G.From_Index (Self_Id, 23);
         Attr_Last : constant G.Type_Ref :=
           G.From_Index (Self_Id, 24);
         Attr_Opaque : constant G.Type_Ref :=
           G.From_Index (Self_Id, 25);
         Attr_Present : constant G.Type_Ref :=
           G.From_Index (Self_Id, 26);
         Attr_Size : constant G.Type_Ref :=
           G.From_Index (Self_Id, 27);
         Attr_Valid : constant G.Type_Ref :=
           G.From_Index (Self_Id, 28);
         Attr_Valid_Checksum : constant G.Type_Ref :=
           G.From_Index (Self_Id, 29);
         Attr_Stmt : constant G.Type_Ref :=
           G.From_Index (Self_Id, 30);
         Attr_Stmt_Append : constant G.Type_Ref :=
           G.From_Index (Self_Id, 31);
         Attr_Stmt_Extend : constant G.Type_Ref :=
           G.From_Index (Self_Id, 32);
         Attr_Stmt_Read : constant G.Type_Ref :=
           G.From_Index (Self_Id, 33);
         Attr_Stmt_Write : constant G.Type_Ref :=
           G.From_Index (Self_Id, 34);
         Base_Aggregate : constant G.Type_Ref :=
           G.From_Index (Self_Id, 35);
         Message_Aggregate_Associations : constant G.Type_Ref :=
           G.From_Index (Self_Id, 36);
         Null_Message_Aggregate : constant G.Type_Ref :=
           G.From_Index (Self_Id, 37);
         Base_Checksum_Val : constant G.Type_Ref :=
           G.From_Index (Self_Id, 38);
         Checksum_Val : constant G.Type_Ref :=
           G.From_Index (Self_Id, 39);
         Checksum_Value_Range : constant G.Type_Ref :=
           G.From_Index (Self_Id, 40);
         Byte_Order_Type : constant G.Type_Ref :=
           G.From_Index (Self_Id, 41);
         Byte_Order_Type_Highorderfirst : constant G.Type_Ref :=
           G.From_Index (Self_Id, 42);
         Byte_Order_Type_Loworderfirst : constant G.Type_Ref :=
           G.From_Index (Self_Id, 43);
         Channel_Attribute : constant G.Type_Ref :=
           G.From_Index (Self_Id, 44);
         Readable : constant G.Type_Ref :=
           G.From_Index (Self_Id, 45);
         Writable : constant G.Type_Ref :=
           G.From_Index (Self_Id, 46);
         Checksum_Assoc : constant G.Type_Ref :=
           G.From_Index (Self_Id, 47);
         Declaration : constant G.Type_Ref :=
           G.From_Index (Self_Id, 48);
         Refinement_Decl : constant G.Type_Ref :=
           G.From_Index (Self_Id, 49);
         Session_Decl : constant G.Type_Ref :=
           G.From_Index (Self_Id, 50);
         Type_Decl : constant G.Type_Ref :=
           G.From_Index (Self_Id, 51);
         Description : constant G.Type_Ref :=
           G.From_Index (Self_Id, 52);
         Element_Value_Assoc : constant G.Type_Ref :=
           G.From_Index (Self_Id, 53);
         Expr : constant G.Type_Ref :=
           G.From_Index (Self_Id, 54);
         Attribute : constant G.Type_Ref :=
           G.From_Index (Self_Id, 55);
         Bin_Op : constant G.Type_Ref :=
           G.From_Index (Self_Id, 56);
         Binding : constant G.Type_Ref :=
           G.From_Index (Self_Id, 57);
         Call : constant G.Type_Ref :=
           G.From_Index (Self_Id, 58);
         Case_Expression : constant G.Type_Ref :=
           G.From_Index (Self_Id, 59);
         Choice : constant G.Type_Ref :=
           G.From_Index (Self_Id, 60);
         Comprehension : constant G.Type_Ref :=
           G.From_Index (Self_Id, 61);
         Context_Item : constant G.Type_Ref :=
           G.From_Index (Self_Id, 62);
         Conversion : constant G.Type_Ref :=
           G.From_Index (Self_Id, 63);
         Message_Aggregate : constant G.Type_Ref :=
           G.From_Index (Self_Id, 64);
         Negation : constant G.Type_Ref :=
           G.From_Index (Self_Id, 65);
         Numeric_Literal : constant G.Type_Ref :=
           G.From_Index (Self_Id, 66);
         Paren_Expression : constant G.Type_Ref :=
           G.From_Index (Self_Id, 67);
         Quantified_Expression : constant G.Type_Ref :=
           G.From_Index (Self_Id, 68);
         Select_Node : constant G.Type_Ref :=
           G.From_Index (Self_Id, 69);
         Sequence_Literal : constant G.Type_Ref :=
           G.From_Index (Self_Id, 70);
         Concatenation : constant G.Type_Ref :=
           G.From_Index (Self_Id, 71);
         Sequence_Aggregate : constant G.Type_Ref :=
           G.From_Index (Self_Id, 72);
         String_Literal : constant G.Type_Ref :=
           G.From_Index (Self_Id, 73);
         Variable : constant G.Type_Ref :=
           G.From_Index (Self_Id, 74);
         Formal_Decl : constant G.Type_Ref :=
           G.From_Index (Self_Id, 75);
         Formal_Channel_Decl : constant G.Type_Ref :=
           G.From_Index (Self_Id, 76);
         Formal_Function_Decl : constant G.Type_Ref :=
           G.From_Index (Self_Id, 77);
         Local_Decl : constant G.Type_Ref :=
           G.From_Index (Self_Id, 78);
         Renaming_Decl : constant G.Type_Ref :=
           G.From_Index (Self_Id, 79);
         Variable_Decl : constant G.Type_Ref :=
           G.From_Index (Self_Id, 80);
         Message_Aggregate_Association : constant G.Type_Ref :=
           G.From_Index (Self_Id, 81);
         Message_Aspect : constant G.Type_Ref :=
           G.From_Index (Self_Id, 82);
         Byte_Order_Aspect : constant G.Type_Ref :=
           G.From_Index (Self_Id, 83);
         Checksum_Aspect : constant G.Type_Ref :=
           G.From_Index (Self_Id, 84);
         Message_Field : constant G.Type_Ref :=
           G.From_Index (Self_Id, 85);
         Message_Fields : constant G.Type_Ref :=
           G.From_Index (Self_Id, 86);
         Null_Message_Field : constant G.Type_Ref :=
           G.From_Index (Self_Id, 87);
         Op : constant G.Type_Ref :=
           G.From_Index (Self_Id, 88);
         Op_Add : constant G.Type_Ref :=
           G.From_Index (Self_Id, 89);
         Op_And : constant G.Type_Ref :=
           G.From_Index (Self_Id, 90);
         Op_Div : constant G.Type_Ref :=
           G.From_Index (Self_Id, 91);
         Op_Eq : constant G.Type_Ref :=
           G.From_Index (Self_Id, 92);
         Op_Ge : constant G.Type_Ref :=
           G.From_Index (Self_Id, 93);
         Op_Gt : constant G.Type_Ref :=
           G.From_Index (Self_Id, 94);
         Op_In : constant G.Type_Ref :=
           G.From_Index (Self_Id, 95);
         Op_Le : constant G.Type_Ref :=
           G.From_Index (Self_Id, 96);
         Op_Lt : constant G.Type_Ref :=
           G.From_Index (Self_Id, 97);
         Op_Mod : constant G.Type_Ref :=
           G.From_Index (Self_Id, 98);
         Op_Mul : constant G.Type_Ref :=
           G.From_Index (Self_Id, 99);
         Op_Neq : constant G.Type_Ref :=
           G.From_Index (Self_Id, 100);
         Op_Notin : constant G.Type_Ref :=
           G.From_Index (Self_Id, 101);
         Op_Or : constant G.Type_Ref :=
           G.From_Index (Self_Id, 102);
         Op_Pow : constant G.Type_Ref :=
           G.From_Index (Self_Id, 103);
         Op_Sub : constant G.Type_Ref :=
           G.From_Index (Self_Id, 104);
         Package_Node : constant G.Type_Ref :=
           G.From_Index (Self_Id, 105);
         Parameter : constant G.Type_Ref :=
           G.From_Index (Self_Id, 106);
         Parameters : constant G.Type_Ref :=
           G.From_Index (Self_Id, 107);
         Quantifier : constant G.Type_Ref :=
           G.From_Index (Self_Id, 108);
         Quantifier_All : constant G.Type_Ref :=
           G.From_Index (Self_Id, 109);
         Quantifier_Some : constant G.Type_Ref :=
           G.From_Index (Self_Id, 110);
         R_F_L_X_Node_Base_List : constant G.Type_Ref :=
           G.From_Index (Self_Id, 111);
         Aspect_List : constant G.Type_Ref :=
           G.From_Index (Self_Id, 112);
         Base_Checksum_Val_List : constant G.Type_Ref :=
           G.From_Index (Self_Id, 113);
         Channel_Attribute_List : constant G.Type_Ref :=
           G.From_Index (Self_Id, 114);
         Checksum_Assoc_List : constant G.Type_Ref :=
           G.From_Index (Self_Id, 115);
         Choice_List : constant G.Type_Ref :=
           G.From_Index (Self_Id, 116);
         Conditional_Transition_List : constant G.Type_Ref :=
           G.From_Index (Self_Id, 117);
         Context_Item_List : constant G.Type_Ref :=
           G.From_Index (Self_Id, 118);
         Declaration_List : constant G.Type_Ref :=
           G.From_Index (Self_Id, 119);
         Element_Value_Assoc_List : constant G.Type_Ref :=
           G.From_Index (Self_Id, 120);
         Expr_List : constant G.Type_Ref :=
           G.From_Index (Self_Id, 121);
         Formal_Decl_List : constant G.Type_Ref :=
           G.From_Index (Self_Id, 122);
         Local_Decl_List : constant G.Type_Ref :=
           G.From_Index (Self_Id, 123);
         Message_Aggregate_Association_List : constant G.Type_Ref :=
           G.From_Index (Self_Id, 124);
         Message_Aspect_List : constant G.Type_Ref :=
           G.From_Index (Self_Id, 125);
         Message_Field_List : constant G.Type_Ref :=
           G.From_Index (Self_Id, 126);
         Numeric_Literal_List : constant G.Type_Ref :=
           G.From_Index (Self_Id, 127);
         Parameter_List : constant G.Type_Ref :=
           G.From_Index (Self_Id, 128);
         R_F_L_X_Node_List : constant G.Type_Ref :=
           G.From_Index (Self_Id, 129);
         State_List : constant G.Type_Ref :=
           G.From_Index (Self_Id, 130);
         Statement_List : constant G.Type_Ref :=
           G.From_Index (Self_Id, 131);
         Term_Assoc_List : constant G.Type_Ref :=
           G.From_Index (Self_Id, 132);
         Then_Node_List : constant G.Type_Ref :=
           G.From_Index (Self_Id, 133);
         Type_Argument_List : constant G.Type_Ref :=
           G.From_Index (Self_Id, 134);
         Unqualified_I_D_List : constant G.Type_Ref :=
           G.From_Index (Self_Id, 135);
         Specification : constant G.Type_Ref :=
           G.From_Index (Self_Id, 136);
         State : constant G.Type_Ref :=
           G.From_Index (Self_Id, 137);
         State_Body : constant G.Type_Ref :=
           G.From_Index (Self_Id, 138);
         Statement : constant G.Type_Ref :=
           G.From_Index (Self_Id, 139);
         Assignment : constant G.Type_Ref :=
           G.From_Index (Self_Id, 140);
         Attribute_Statement : constant G.Type_Ref :=
           G.From_Index (Self_Id, 141);
         Message_Field_Assignment : constant G.Type_Ref :=
           G.From_Index (Self_Id, 142);
         Reset : constant G.Type_Ref :=
           G.From_Index (Self_Id, 143);
         Term_Assoc : constant G.Type_Ref :=
           G.From_Index (Self_Id, 144);
         Then_Node : constant G.Type_Ref :=
           G.From_Index (Self_Id, 145);
         Transition : constant G.Type_Ref :=
           G.From_Index (Self_Id, 146);
         Conditional_Transition : constant G.Type_Ref :=
           G.From_Index (Self_Id, 147);
         Type_Argument : constant G.Type_Ref :=
           G.From_Index (Self_Id, 148);
         Type_Def : constant G.Type_Ref :=
           G.From_Index (Self_Id, 149);
         Abstract_Message_Type_Def : constant G.Type_Ref :=
           G.From_Index (Self_Id, 150);
         Message_Type_Def : constant G.Type_Ref :=
           G.From_Index (Self_Id, 151);
         Null_Message_Type_Def : constant G.Type_Ref :=
           G.From_Index (Self_Id, 152);
         Enumeration_Def : constant G.Type_Ref :=
           G.From_Index (Self_Id, 153);
         Named_Enumeration_Def : constant G.Type_Ref :=
           G.From_Index (Self_Id, 154);
         Positional_Enumeration_Def : constant G.Type_Ref :=
           G.From_Index (Self_Id, 155);
         Enumeration_Type_Def : constant G.Type_Ref :=
           G.From_Index (Self_Id, 156);
         Integer_Type_Def : constant G.Type_Ref :=
           G.From_Index (Self_Id, 157);
         Modular_Type_Def : constant G.Type_Ref :=
           G.From_Index (Self_Id, 158);
         Range_Type_Def : constant G.Type_Ref :=
           G.From_Index (Self_Id, 159);
         Sequence_Type_Def : constant G.Type_Ref :=
           G.From_Index (Self_Id, 160);
         Type_Derivation_Def : constant G.Type_Ref :=
           G.From_Index (Self_Id, 161);
   end Type_Refs;

   -----------------------
   -- Member references --
   -----------------------

   package Member_Refs is
         I_D_F_Package : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 1);
         I_D_F_Name : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 2);
         Aspect_F_Identifier : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 3);
         Aspect_F_Value : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 4);
         Message_Aggregate_Associations_F_Associations : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 5);
         Checksum_Val_F_Data : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 6);
         Checksum_Value_Range_F_First : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 7);
         Checksum_Value_Range_F_Last : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 8);
         Checksum_Assoc_F_Identifier : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 9);
         Checksum_Assoc_F_Covered_Fields : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 10);
         Refinement_Decl_F_Pdu : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 11);
         Refinement_Decl_F_Field : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 12);
         Refinement_Decl_F_Sdu : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 13);
         Refinement_Decl_F_Condition : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 14);
         Session_Decl_F_Parameters : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 15);
         Session_Decl_F_Identifier : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 16);
         Session_Decl_F_Declarations : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 17);
         Session_Decl_F_States : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 18);
         Session_Decl_F_End_Identifier : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 19);
         Type_Decl_F_Identifier : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 20);
         Type_Decl_F_Parameters : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 21);
         Type_Decl_F_Definition : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 22);
         Description_F_Content : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 23);
         Element_Value_Assoc_F_Identifier : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 24);
         Element_Value_Assoc_F_Literal : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 25);
         Attribute_F_Expression : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 26);
         Attribute_F_Kind : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 27);
         Bin_Op_F_Left : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 28);
         Bin_Op_F_Op : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 29);
         Bin_Op_F_Right : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 30);
         Binding_F_Expression : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 31);
         Binding_F_Bindings : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 32);
         Call_F_Identifier : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 33);
         Call_F_Arguments : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 34);
         Case_Expression_F_Expression : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 35);
         Case_Expression_F_Choices : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 36);
         Choice_F_Selectors : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 37);
         Choice_F_Expression : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 38);
         Comprehension_F_Iterator : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 39);
         Comprehension_F_Sequence : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 40);
         Comprehension_F_Condition : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 41);
         Comprehension_F_Selector : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 42);
         Context_Item_F_Item : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 43);
         Conversion_F_Target_Identifier : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 44);
         Conversion_F_Argument : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 45);
         Message_Aggregate_F_Identifier : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 46);
         Message_Aggregate_F_Values : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 47);
         Negation_F_Data : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 48);
         Paren_Expression_F_Data : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 49);
         Quantified_Expression_F_Operation : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 50);
         Quantified_Expression_F_Parameter_Identifier : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 51);
         Quantified_Expression_F_Iterable : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 52);
         Quantified_Expression_F_Predicate : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 53);
         Select_Node_F_Expression : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 54);
         Select_Node_F_Selector : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 55);
         Concatenation_F_Left : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 56);
         Concatenation_F_Right : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 57);
         Sequence_Aggregate_F_Values : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 58);
         Variable_F_Identifier : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 59);
         Formal_Channel_Decl_F_Identifier : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 60);
         Formal_Channel_Decl_F_Parameters : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 61);
         Formal_Function_Decl_F_Identifier : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 62);
         Formal_Function_Decl_F_Parameters : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 63);
         Formal_Function_Decl_F_Return_Type_Identifier : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 64);
         Renaming_Decl_F_Identifier : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 65);
         Renaming_Decl_F_Type_Identifier : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 66);
         Renaming_Decl_F_Expression : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 67);
         Variable_Decl_F_Identifier : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 68);
         Variable_Decl_F_Type_Identifier : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 69);
         Variable_Decl_F_Initializer : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 70);
         Message_Aggregate_Association_F_Identifier : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 71);
         Message_Aggregate_Association_F_Expression : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 72);
         Byte_Order_Aspect_F_Byte_Order : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 73);
         Checksum_Aspect_F_Associations : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 74);
         Message_Field_F_Identifier : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 75);
         Message_Field_F_Type_Identifier : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 76);
         Message_Field_F_Type_Arguments : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 77);
         Message_Field_F_Aspects : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 78);
         Message_Field_F_Condition : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 79);
         Message_Field_F_Thens : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 80);
         Message_Fields_F_Initial_Field : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 81);
         Message_Fields_F_Fields : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 82);
         Null_Message_Field_F_Then : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 83);
         Package_Node_F_Identifier : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 84);
         Package_Node_F_Declarations : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 85);
         Package_Node_F_End_Identifier : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 86);
         Parameter_F_Identifier : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 87);
         Parameter_F_Type_Identifier : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 88);
         Parameters_F_Parameters : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 89);
         Specification_F_Context_Clause : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 90);
         Specification_F_Package_Declaration : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 91);
         State_F_Identifier : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 92);
         State_F_Description : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 93);
         State_F_Body : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 94);
         State_Body_F_Declarations : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 95);
         State_Body_F_Actions : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 96);
         State_Body_F_Conditional_Transitions : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 97);
         State_Body_F_Final_Transition : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 98);
         State_Body_F_Exception_Transition : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 99);
         State_Body_F_End_Identifier : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 100);
         Assignment_F_Identifier : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 101);
         Assignment_F_Expression : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 102);
         Attribute_Statement_F_Identifier : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 103);
         Attribute_Statement_F_Attr : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 104);
         Attribute_Statement_F_Expression : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 105);
         Message_Field_Assignment_F_Message : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 106);
         Message_Field_Assignment_F_Field : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 107);
         Message_Field_Assignment_F_Expression : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 108);
         Reset_F_Identifier : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 109);
         Reset_F_Associations : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 110);
         Term_Assoc_F_Identifier : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 111);
         Term_Assoc_F_Expression : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 112);
         Then_Node_F_Target : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 113);
         Then_Node_F_Aspects : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 114);
         Then_Node_F_Condition : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 115);
         Transition_F_Target : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 116);
         Transition_F_Description : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 117);
         Conditional_Transition_F_Condition : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 118);
         Type_Argument_F_Identifier : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 119);
         Type_Argument_F_Expression : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 120);
         Message_Type_Def_F_Message_Fields : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 121);
         Message_Type_Def_F_Aspects : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 122);
         Named_Enumeration_Def_F_Elements : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 123);
         Positional_Enumeration_Def_F_Elements : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 124);
         Enumeration_Type_Def_F_Elements : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 125);
         Enumeration_Type_Def_F_Aspects : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 126);
         Modular_Type_Def_F_Mod : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 127);
         Range_Type_Def_F_First : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 128);
         Range_Type_Def_F_Last : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 129);
         Range_Type_Def_F_Size : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 130);
         Sequence_Type_Def_F_Element_Type : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 131);
         Type_Derivation_Def_F_Base : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 132);
         Parent : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 133);
         Parents : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 134);
         Children : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 135);
         Token_Start : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 136);
         Token_End : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 137);
         Child_Index : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 138);
         Previous_Sibling : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 139);
         Next_Sibling : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 140);
         Unit : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 141);
         Is_Ghost : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 142);
         Full_Sloc_Image : constant G.Struct_Member_Ref :=
           G.From_Index (Self_Id, 143);
   end Member_Refs;

end Librflxlang.Generic_API.Introspection;
