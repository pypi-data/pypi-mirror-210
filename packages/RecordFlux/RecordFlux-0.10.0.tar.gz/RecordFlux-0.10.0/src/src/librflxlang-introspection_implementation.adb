


package body Librflxlang.Introspection_Implementation is

   ----------------
   -- As_Boolean --
   ----------------

   function As_Boolean (Self : Internal_Value) return Boolean is
   begin
      return Self.Boolean_Value;
   end As_Boolean;

   ----------------
   -- As_Integer --
   ----------------

   function As_Integer (Self : Internal_Value) return Integer is
   begin
      return Self.Integer_Value;
   end As_Integer;

   ------------------
   -- As_Character --
   ------------------

   function As_Character (Self : Internal_Value) return Character_Type is
   begin
      return Self.Character_Value;
   end As_Character;

   ---------------
   -- As_String --
   ---------------

   function As_String (Self : Internal_Value) return String_Type is
   begin
      return Self.String_Value;
   end As_String;

   -------------
   -- As_Node --
   -------------

   function As_Node (Self : Internal_Value) return Internal_Entity is
   begin
      return Self.Node_Value;
   end As_Node;

      function As_Analysis_Unit_Kind
        (Self : Internal_Value) return Analysis_Unit_Kind is
      begin
         return Self.Analysis_Unit_Kind_Value;
      end As_Analysis_Unit_Kind;

      function As_Lookup_Kind
        (Self : Internal_Value) return Lookup_Kind is
      begin
         return Self.Lookup_Kind_Value;
      end As_Lookup_Kind;

      function As_Designated_Env_Kind
        (Self : Internal_Value) return Designated_Env_Kind is
      begin
         return Self.Designated_Env_Kind_Value;
      end As_Designated_Env_Kind;

      function As_Grammar_Rule
        (Self : Internal_Value) return Grammar_Rule is
      begin
         return Self.Grammar_Rule_Value;
      end As_Grammar_Rule;


   --  Now we can emit descriptor tables

   ----------------------
   -- Struct_Type_Desc --
   ----------------------

   function Struct_Type_Desc
     (Kind : Struct_Value_Kind) return Struct_Type_Descriptor_Access
   is
   begin
         pragma Unreferenced (Kind);
         return (raise Program_Error);
   end Struct_Type_Desc;

   -----------------------
   -- Struct_Field_Name --
   -----------------------

   function Struct_Field_Name (Field : Struct_Field_Reference) return Text_Type
   is
   begin
      pragma Warnings (Off, "value not in range of subtype");
      return To_Text (Struct_Field_Descriptors (Field).Name);
      pragma Warnings (On, "value not in range of subtype");
   end Struct_Field_Name;

   -----------------------
   -- Struct_Field_Type --
   -----------------------

   function Struct_Field_Type
     (Field : Struct_Field_Reference) return Type_Constraint is
   begin
      pragma Warnings (Off, "value not in range of subtype");
      return Struct_Field_Descriptors (Field).Field_Type;
      pragma Warnings (On, "value not in range of subtype");
   end Struct_Field_Type;

   -------------------
   -- Struct_Fields --
   -------------------

   pragma Warnings (Off, "referenced");
   function Struct_Fields
     (Kind : Struct_Value_Kind) return Struct_Field_Reference_Array
   is
      pragma Warnings (On, "referenced");
   begin
         return (raise Program_Error);
   end Struct_Fields;

   --------------
   -- DSL_Name --
   --------------

   function DSL_Name (Id : Node_Type_Id) return Text_Type is
   begin
      return To_Text (To_String (Node_Type_Descriptors (Id).DSL_Name));
   end DSL_Name;

   ---------------------
   -- Lookup_DSL_Name --
   ---------------------

   function Lookup_DSL_Name (Name : Text_Type) return Any_Node_Type_Id is
      use Node_Type_Id_Maps;

      Position : constant Cursor :=
         DSL_Name_To_Node_Type.Find (To_Unbounded_String (Image (Name)));
   begin
      if Has_Element (Position) then
         return Element (Position);
      else
         return None;
      end if;
   end Lookup_DSL_Name;

   -----------------
   -- Is_Abstract --
   -----------------

   function Is_Abstract (Id : Node_Type_Id) return Boolean is
   begin
      return Node_Type_Descriptors (Id).Is_Abstract;
   end Is_Abstract;

   --------------
   -- Kind_For --
   --------------

   function Kind_For (Id : Node_Type_Id) return R_F_L_X_Node_Kind_Type is
      Desc : Node_Type_Descriptor renames Node_Type_Descriptors (Id).all;
   begin
      if Desc.Is_Abstract then
         raise Bad_Type_Error with "trying to get kind for abstract node";
      end if;
      return Desc.Kind;
   end Kind_For;

   --------------------
   -- First_Kind_For --
   --------------------

   function First_Kind_For (Id : Node_Type_Id) return R_F_L_X_Node_Kind_Type is

      --  Look for the leftmost leaf derivation of an abstract node. Langkit
      --  disallows abstract nodes with no concrete derivation, so each time we
      --  see an an abstract node, we know there are concrete derivations down
      --  the tree.
      --
      --  Note that we have to stop at the first concrete node we see because
      --  of the way we sort kinds: the kind of concrete root comes before the
      --  kinds of all its derivations.

      Cur : Node_Type_Id := Id;
   begin
      loop
         declare
            Desc : Node_Type_Descriptor renames
               Node_Type_Descriptors (Cur).all;
         begin
            exit when not Desc.Is_Abstract or else Desc.Derivations'Length = 0;
            Cur := Desc.Derivations (Desc.Derivations'First);
         end;
      end loop;
      return Kind_For (Cur);
   end First_Kind_For;

   -------------------
   -- Last_Kind_For --
   -------------------

   function Last_Kind_For (Id : Node_Type_Id) return R_F_L_X_Node_Kind_Type is

      --  Look for the rightmost leaf derivation. Langkit disallows abstract
      --  nodes with no concrete derivation, so we know that the result is
      --  concrete.

      Cur : Node_Type_Id := Id;
   begin
      loop
         declare
            Desc : Node_Type_Descriptor renames
               Node_Type_Descriptors (Cur).all;
         begin
            exit when Desc.Derivations'Length = 0;
            Cur := Desc.Derivations (Desc.Derivations'Last);
         end;
      end loop;
      return Kind_For (Cur);
   end Last_Kind_For;

   -----------------
   -- Id_For_Kind --
   -----------------

   function Id_For_Kind (Kind : R_F_L_X_Node_Kind_Type) return Node_Type_Id is
   begin
      return Kind_To_Id (Kind);
   end Id_For_Kind;

   ------------------
   -- Is_Root_Node --
   ------------------

   function Is_Root_Node (Id : Node_Type_Id) return Boolean is
   begin
      return Id = Common.R_F_L_X_Node_Type_Id;
   end Is_Root_Node;

   ---------------
   -- Base_Type --
   ---------------

   function Base_Type (Id : Node_Type_Id) return Node_Type_Id is
   begin
      if Is_Root_Node (Id) then
         raise Bad_Type_Error with "trying to get base type of root node";
      end if;
      return Node_Type_Descriptors (Id).Base_Type;
   end Base_Type;

   -------------------
   -- Derived_Types --
   -------------------

   function Derived_Types (Id : Node_Type_Id) return Node_Type_Id_Array is
   begin
      return Node_Type_Descriptors (Id).Derivations;
   end Derived_Types;

   ---------------------
   -- Is_Derived_From --
   ---------------------

   function Is_Derived_From (Id, Parent : Node_Type_Id) return Boolean is
      Cursor : Any_Node_Type_Id := Id;
   begin
      while Cursor /= None loop
         if Cursor = Parent then
            return True;
         end if;

         Cursor := Node_Type_Descriptors (Cursor).Base_Type;
      end loop;
      return False;
   end Is_Derived_From;

   -----------------
   -- Member_Name --
   -----------------

   function Member_Name (Member : Member_Reference) return Text_Type is
   begin
      case Member is
         when Struct_Field_Reference =>
            pragma Warnings (Off, "value not in range of type");
            return Struct_Field_Name (Member);
            pragma Warnings (On, "value not in range of type");

         when Syntax_Field_Reference =>
            pragma Warnings (Off, "value not in range of type");
            return Syntax_Field_Name (Member);
            pragma Warnings (On, "value not in range of type");

         when Property_Reference =>
            return Property_Name (Member);
      end case;
   end Member_Name;

   -----------------
   -- Member_Type --
   -----------------

   function Member_Type (Member : Member_Reference) return Type_Constraint is
   begin
      case Member is
         when Struct_Field_Reference =>
            pragma Warnings (Off, "value not in range of type");
            return Struct_Field_Type (Member);
            pragma Warnings (On, "value not in range of type");

         when Syntax_Field_Reference =>
            pragma Warnings (Off, "value not in range of type");
            return (Kind      => Node_Value,
                    Node_Type => Syntax_Field_Type (Member));
            pragma Warnings (On, "value not in range of type");

         when Property_Reference =>
            return Property_Return_Type (Member);
      end case;
   end Member_Type;

   --------------------------
   -- Lookup_Member_Struct --
   --------------------------

   function Lookup_Member_Struct
     (Kind : Struct_Value_Kind;
      Name : Text_Type) return Any_Member_Reference
   is
      pragma Warnings (Off, "value not in range of type");
      Desc : Struct_Type_Descriptor renames Struct_Type_Desc (Kind).all;
      pragma Warnings (On, "value not in range of type");
   begin
      for F of Desc.Fields loop
         if To_Text (F.Name) = Name then
            return F.Reference;
         end if;
      end loop;

      return None;
   end Lookup_Member_Struct;

   ------------------------
   -- Lookup_Member_Node --
   ------------------------

   function Lookup_Member_Node
     (Id   : Node_Type_Id;
      Name : Text_Type) return Any_Member_Reference
   is
      Cursor : Any_Node_Type_Id := Id;
   begin
      --  Go through the derivation chain for Id and look for any field or
      --  property whose name matches Name.

      while Cursor /= None loop
         declare
            Node_Desc : Node_Type_Descriptor renames
               Node_Type_Descriptors (Cursor).all;
         begin
            for F of Node_Desc.Fields loop
               pragma Warnings (Off, "value not in range of type");
               if Syntax_Field_Name (F.Field) = Name then
                  return F.Field;
               end if;
               pragma Warnings (On, "value not in range of type");
            end loop;

            for P of Node_Desc.Properties loop
               if Property_Name (P) = Name then
                  return P;
               end if;
            end loop;

            Cursor := Node_Desc.Base_Type;
         end;
      end loop;
      return None;
   end Lookup_Member_Node;

   -----------------------
   -- Syntax_Field_Name --
   -----------------------

   function Syntax_Field_Name (Field : Syntax_Field_Reference) return Text_Type
   is
   begin
      pragma Warnings (Off, "value not in range of subtype");
      return To_Text (Syntax_Field_Descriptors (Field).Name);
      pragma Warnings (On, "value not in range of subtype");
   end Syntax_Field_Name;

   -----------------------
   -- Syntax_Field_Type --
   -----------------------

   function Syntax_Field_Type
     (Field : Syntax_Field_Reference) return Node_Type_Id is
   begin
      pragma Warnings (Off, "value not in range of subtype");
      return Syntax_Field_Descriptors (Field).Field_Type;
      pragma Warnings (On, "value not in range of subtype");
   end Syntax_Field_Type;

   -----------------------
   -- Eval_Syntax_Field --
   -----------------------

   function Eval_Syntax_Field
     (Node  : Bare_R_F_L_X_Node;
      Field : Syntax_Field_Reference) return Bare_R_F_L_X_Node
   is
      Kind : constant R_F_L_X_Node_Kind_Type := Node.Kind;
   begin
      
      case Rflx_R_F_L_X_Node (Kind) is
when Rflx_I_D_Range =>
declare
N_Bare_I_D : constant Bare_I_D := Node;
begin
case Field is
when I_D_F_Package => return I_D_F_Package (N_Bare_I_D);
when I_D_F_Name => return I_D_F_Name (N_Bare_I_D);
when others => null;
end case;
end;
when Rflx_Aspect_Range =>
declare
N_Bare_Aspect : constant Bare_Aspect := Node;
begin
case Field is
when Aspect_F_Identifier => return Aspect_F_Identifier (N_Bare_Aspect);
when Aspect_F_Value => return Aspect_F_Value (N_Bare_Aspect);
when others => null;
end case;
end;
when Rflx_Message_Aggregate_Associations_Range =>
declare
N_Bare_Message_Aggregate_Associations : constant Bare_Message_Aggregate_Associations := Node;
begin
case Field is
when Message_Aggregate_Associations_F_Associations => return Message_Aggregate_Associations_F_Associations (N_Bare_Message_Aggregate_Associations);
when others => null;
end case;
end;
when Rflx_Checksum_Val_Range =>
declare
N_Bare_Checksum_Val : constant Bare_Checksum_Val := Node;
begin
case Field is
when Checksum_Val_F_Data => return Checksum_Val_F_Data (N_Bare_Checksum_Val);
when others => null;
end case;
end;
when Rflx_Checksum_Value_Range_Range =>
declare
N_Bare_Checksum_Value_Range : constant Bare_Checksum_Value_Range := Node;
begin
case Field is
when Checksum_Value_Range_F_First => return Checksum_Value_Range_F_First (N_Bare_Checksum_Value_Range);
when Checksum_Value_Range_F_Last => return Checksum_Value_Range_F_Last (N_Bare_Checksum_Value_Range);
when others => null;
end case;
end;
when Rflx_Checksum_Assoc_Range =>
declare
N_Bare_Checksum_Assoc : constant Bare_Checksum_Assoc := Node;
begin
case Field is
when Checksum_Assoc_F_Identifier => return Checksum_Assoc_F_Identifier (N_Bare_Checksum_Assoc);
when Checksum_Assoc_F_Covered_Fields => return Checksum_Assoc_F_Covered_Fields (N_Bare_Checksum_Assoc);
when others => null;
end case;
end;
when Rflx_Refinement_Decl_Range =>
declare
N_Bare_Refinement_Decl : constant Bare_Refinement_Decl := Node;
begin
case Field is
when Refinement_Decl_F_Pdu => return Refinement_Decl_F_Pdu (N_Bare_Refinement_Decl);
when Refinement_Decl_F_Field => return Refinement_Decl_F_Field (N_Bare_Refinement_Decl);
when Refinement_Decl_F_Sdu => return Refinement_Decl_F_Sdu (N_Bare_Refinement_Decl);
when Refinement_Decl_F_Condition => return Refinement_Decl_F_Condition (N_Bare_Refinement_Decl);
when others => null;
end case;
end;
when Rflx_Session_Decl_Range =>
declare
N_Bare_Session_Decl : constant Bare_Session_Decl := Node;
begin
case Field is
when Session_Decl_F_Parameters => return Session_Decl_F_Parameters (N_Bare_Session_Decl);
when Session_Decl_F_Identifier => return Session_Decl_F_Identifier (N_Bare_Session_Decl);
when Session_Decl_F_Declarations => return Session_Decl_F_Declarations (N_Bare_Session_Decl);
when Session_Decl_F_States => return Session_Decl_F_States (N_Bare_Session_Decl);
when Session_Decl_F_End_Identifier => return Session_Decl_F_End_Identifier (N_Bare_Session_Decl);
when others => null;
end case;
end;
when Rflx_Type_Decl_Range =>
declare
N_Bare_Type_Decl : constant Bare_Type_Decl := Node;
begin
case Field is
when Type_Decl_F_Identifier => return Type_Decl_F_Identifier (N_Bare_Type_Decl);
when Type_Decl_F_Parameters => return Type_Decl_F_Parameters (N_Bare_Type_Decl);
when Type_Decl_F_Definition => return Type_Decl_F_Definition (N_Bare_Type_Decl);
when others => null;
end case;
end;
when Rflx_Description_Range =>
declare
N_Bare_Description : constant Bare_Description := Node;
begin
case Field is
when Description_F_Content => return Description_F_Content (N_Bare_Description);
when others => null;
end case;
end;
when Rflx_Element_Value_Assoc_Range =>
declare
N_Bare_Element_Value_Assoc : constant Bare_Element_Value_Assoc := Node;
begin
case Field is
when Element_Value_Assoc_F_Identifier => return Element_Value_Assoc_F_Identifier (N_Bare_Element_Value_Assoc);
when Element_Value_Assoc_F_Literal => return Element_Value_Assoc_F_Literal (N_Bare_Element_Value_Assoc);
when others => null;
end case;
end;
when Rflx_Attribute_Range =>
declare
N_Bare_Attribute : constant Bare_Attribute := Node;
begin
case Field is
when Attribute_F_Expression => return Attribute_F_Expression (N_Bare_Attribute);
when Attribute_F_Kind => return Attribute_F_Kind (N_Bare_Attribute);
when others => null;
end case;
end;
when Rflx_Bin_Op_Range =>
declare
N_Bare_Bin_Op : constant Bare_Bin_Op := Node;
begin
case Field is
when Bin_Op_F_Left => return Bin_Op_F_Left (N_Bare_Bin_Op);
when Bin_Op_F_Op => return Bin_Op_F_Op (N_Bare_Bin_Op);
when Bin_Op_F_Right => return Bin_Op_F_Right (N_Bare_Bin_Op);
when others => null;
end case;
end;
when Rflx_Binding_Range =>
declare
N_Bare_Binding : constant Bare_Binding := Node;
begin
case Field is
when Binding_F_Expression => return Binding_F_Expression (N_Bare_Binding);
when Binding_F_Bindings => return Binding_F_Bindings (N_Bare_Binding);
when others => null;
end case;
end;
when Rflx_Call_Range =>
declare
N_Bare_Call : constant Bare_Call := Node;
begin
case Field is
when Call_F_Identifier => return Call_F_Identifier (N_Bare_Call);
when Call_F_Arguments => return Call_F_Arguments (N_Bare_Call);
when others => null;
end case;
end;
when Rflx_Case_Expression_Range =>
declare
N_Bare_Case_Expression : constant Bare_Case_Expression := Node;
begin
case Field is
when Case_Expression_F_Expression => return Case_Expression_F_Expression (N_Bare_Case_Expression);
when Case_Expression_F_Choices => return Case_Expression_F_Choices (N_Bare_Case_Expression);
when others => null;
end case;
end;
when Rflx_Choice_Range =>
declare
N_Bare_Choice : constant Bare_Choice := Node;
begin
case Field is
when Choice_F_Selectors => return Choice_F_Selectors (N_Bare_Choice);
when Choice_F_Expression => return Choice_F_Expression (N_Bare_Choice);
when others => null;
end case;
end;
when Rflx_Comprehension_Range =>
declare
N_Bare_Comprehension : constant Bare_Comprehension := Node;
begin
case Field is
when Comprehension_F_Iterator => return Comprehension_F_Iterator (N_Bare_Comprehension);
when Comprehension_F_Sequence => return Comprehension_F_Sequence (N_Bare_Comprehension);
when Comprehension_F_Condition => return Comprehension_F_Condition (N_Bare_Comprehension);
when Comprehension_F_Selector => return Comprehension_F_Selector (N_Bare_Comprehension);
when others => null;
end case;
end;
when Rflx_Context_Item_Range =>
declare
N_Bare_Context_Item : constant Bare_Context_Item := Node;
begin
case Field is
when Context_Item_F_Item => return Context_Item_F_Item (N_Bare_Context_Item);
when others => null;
end case;
end;
when Rflx_Conversion_Range =>
declare
N_Bare_Conversion : constant Bare_Conversion := Node;
begin
case Field is
when Conversion_F_Target_Identifier => return Conversion_F_Target_Identifier (N_Bare_Conversion);
when Conversion_F_Argument => return Conversion_F_Argument (N_Bare_Conversion);
when others => null;
end case;
end;
when Rflx_Message_Aggregate_Range =>
declare
N_Bare_Message_Aggregate : constant Bare_Message_Aggregate := Node;
begin
case Field is
when Message_Aggregate_F_Identifier => return Message_Aggregate_F_Identifier (N_Bare_Message_Aggregate);
when Message_Aggregate_F_Values => return Message_Aggregate_F_Values (N_Bare_Message_Aggregate);
when others => null;
end case;
end;
when Rflx_Negation_Range =>
declare
N_Bare_Negation : constant Bare_Negation := Node;
begin
case Field is
when Negation_F_Data => return Negation_F_Data (N_Bare_Negation);
when others => null;
end case;
end;
when Rflx_Paren_Expression_Range =>
declare
N_Bare_Paren_Expression : constant Bare_Paren_Expression := Node;
begin
case Field is
when Paren_Expression_F_Data => return Paren_Expression_F_Data (N_Bare_Paren_Expression);
when others => null;
end case;
end;
when Rflx_Quantified_Expression_Range =>
declare
N_Bare_Quantified_Expression : constant Bare_Quantified_Expression := Node;
begin
case Field is
when Quantified_Expression_F_Operation => return Quantified_Expression_F_Operation (N_Bare_Quantified_Expression);
when Quantified_Expression_F_Parameter_Identifier => return Quantified_Expression_F_Parameter_Identifier (N_Bare_Quantified_Expression);
when Quantified_Expression_F_Iterable => return Quantified_Expression_F_Iterable (N_Bare_Quantified_Expression);
when Quantified_Expression_F_Predicate => return Quantified_Expression_F_Predicate (N_Bare_Quantified_Expression);
when others => null;
end case;
end;
when Rflx_Select_Node_Range =>
declare
N_Bare_Select_Node : constant Bare_Select_Node := Node;
begin
case Field is
when Select_Node_F_Expression => return Select_Node_F_Expression (N_Bare_Select_Node);
when Select_Node_F_Selector => return Select_Node_F_Selector (N_Bare_Select_Node);
when others => null;
end case;
end;
when Rflx_Concatenation_Range =>
declare
N_Bare_Concatenation : constant Bare_Concatenation := Node;
begin
case Field is
when Concatenation_F_Left => return Concatenation_F_Left (N_Bare_Concatenation);
when Concatenation_F_Right => return Concatenation_F_Right (N_Bare_Concatenation);
when others => null;
end case;
end;
when Rflx_Sequence_Aggregate_Range =>
declare
N_Bare_Sequence_Aggregate : constant Bare_Sequence_Aggregate := Node;
begin
case Field is
when Sequence_Aggregate_F_Values => return Sequence_Aggregate_F_Values (N_Bare_Sequence_Aggregate);
when others => null;
end case;
end;
when Rflx_Variable_Range =>
declare
N_Bare_Variable : constant Bare_Variable := Node;
begin
case Field is
when Variable_F_Identifier => return Variable_F_Identifier (N_Bare_Variable);
when others => null;
end case;
end;
when Rflx_Formal_Channel_Decl_Range =>
declare
N_Bare_Formal_Channel_Decl : constant Bare_Formal_Channel_Decl := Node;
begin
case Field is
when Formal_Channel_Decl_F_Identifier => return Formal_Channel_Decl_F_Identifier (N_Bare_Formal_Channel_Decl);
when Formal_Channel_Decl_F_Parameters => return Formal_Channel_Decl_F_Parameters (N_Bare_Formal_Channel_Decl);
when others => null;
end case;
end;
when Rflx_Formal_Function_Decl_Range =>
declare
N_Bare_Formal_Function_Decl : constant Bare_Formal_Function_Decl := Node;
begin
case Field is
when Formal_Function_Decl_F_Identifier => return Formal_Function_Decl_F_Identifier (N_Bare_Formal_Function_Decl);
when Formal_Function_Decl_F_Parameters => return Formal_Function_Decl_F_Parameters (N_Bare_Formal_Function_Decl);
when Formal_Function_Decl_F_Return_Type_Identifier => return Formal_Function_Decl_F_Return_Type_Identifier (N_Bare_Formal_Function_Decl);
when others => null;
end case;
end;
when Rflx_Renaming_Decl_Range =>
declare
N_Bare_Renaming_Decl : constant Bare_Renaming_Decl := Node;
begin
case Field is
when Renaming_Decl_F_Identifier => return Renaming_Decl_F_Identifier (N_Bare_Renaming_Decl);
when Renaming_Decl_F_Type_Identifier => return Renaming_Decl_F_Type_Identifier (N_Bare_Renaming_Decl);
when Renaming_Decl_F_Expression => return Renaming_Decl_F_Expression (N_Bare_Renaming_Decl);
when others => null;
end case;
end;
when Rflx_Variable_Decl_Range =>
declare
N_Bare_Variable_Decl : constant Bare_Variable_Decl := Node;
begin
case Field is
when Variable_Decl_F_Identifier => return Variable_Decl_F_Identifier (N_Bare_Variable_Decl);
when Variable_Decl_F_Type_Identifier => return Variable_Decl_F_Type_Identifier (N_Bare_Variable_Decl);
when Variable_Decl_F_Initializer => return Variable_Decl_F_Initializer (N_Bare_Variable_Decl);
when others => null;
end case;
end;
when Rflx_Message_Aggregate_Association_Range =>
declare
N_Bare_Message_Aggregate_Association : constant Bare_Message_Aggregate_Association := Node;
begin
case Field is
when Message_Aggregate_Association_F_Identifier => return Message_Aggregate_Association_F_Identifier (N_Bare_Message_Aggregate_Association);
when Message_Aggregate_Association_F_Expression => return Message_Aggregate_Association_F_Expression (N_Bare_Message_Aggregate_Association);
when others => null;
end case;
end;
when Rflx_Byte_Order_Aspect_Range =>
declare
N_Bare_Byte_Order_Aspect : constant Bare_Byte_Order_Aspect := Node;
begin
case Field is
when Byte_Order_Aspect_F_Byte_Order => return Byte_Order_Aspect_F_Byte_Order (N_Bare_Byte_Order_Aspect);
when others => null;
end case;
end;
when Rflx_Checksum_Aspect_Range =>
declare
N_Bare_Checksum_Aspect : constant Bare_Checksum_Aspect := Node;
begin
case Field is
when Checksum_Aspect_F_Associations => return Checksum_Aspect_F_Associations (N_Bare_Checksum_Aspect);
when others => null;
end case;
end;
when Rflx_Message_Field_Range =>
declare
N_Bare_Message_Field : constant Bare_Message_Field := Node;
begin
case Field is
when Message_Field_F_Identifier => return Message_Field_F_Identifier (N_Bare_Message_Field);
when Message_Field_F_Type_Identifier => return Message_Field_F_Type_Identifier (N_Bare_Message_Field);
when Message_Field_F_Type_Arguments => return Message_Field_F_Type_Arguments (N_Bare_Message_Field);
when Message_Field_F_Aspects => return Message_Field_F_Aspects (N_Bare_Message_Field);
when Message_Field_F_Condition => return Message_Field_F_Condition (N_Bare_Message_Field);
when Message_Field_F_Thens => return Message_Field_F_Thens (N_Bare_Message_Field);
when others => null;
end case;
end;
when Rflx_Message_Fields_Range =>
declare
N_Bare_Message_Fields : constant Bare_Message_Fields := Node;
begin
case Field is
when Message_Fields_F_Initial_Field => return Message_Fields_F_Initial_Field (N_Bare_Message_Fields);
when Message_Fields_F_Fields => return Message_Fields_F_Fields (N_Bare_Message_Fields);
when others => null;
end case;
end;
when Rflx_Null_Message_Field_Range =>
declare
N_Bare_Null_Message_Field : constant Bare_Null_Message_Field := Node;
begin
case Field is
when Null_Message_Field_F_Then => return Null_Message_Field_F_Then (N_Bare_Null_Message_Field);
when others => null;
end case;
end;
when Rflx_Package_Node_Range =>
declare
N_Bare_Package_Node : constant Bare_Package_Node := Node;
begin
case Field is
when Package_Node_F_Identifier => return Package_Node_F_Identifier (N_Bare_Package_Node);
when Package_Node_F_Declarations => return Package_Node_F_Declarations (N_Bare_Package_Node);
when Package_Node_F_End_Identifier => return Package_Node_F_End_Identifier (N_Bare_Package_Node);
when others => null;
end case;
end;
when Rflx_Parameter_Range =>
declare
N_Bare_Parameter : constant Bare_Parameter := Node;
begin
case Field is
when Parameter_F_Identifier => return Parameter_F_Identifier (N_Bare_Parameter);
when Parameter_F_Type_Identifier => return Parameter_F_Type_Identifier (N_Bare_Parameter);
when others => null;
end case;
end;
when Rflx_Parameters_Range =>
declare
N_Bare_Parameters : constant Bare_Parameters := Node;
begin
case Field is
when Parameters_F_Parameters => return Parameters_F_Parameters (N_Bare_Parameters);
when others => null;
end case;
end;
when Rflx_Specification_Range =>
declare
N_Bare_Specification : constant Bare_Specification := Node;
begin
case Field is
when Specification_F_Context_Clause => return Specification_F_Context_Clause (N_Bare_Specification);
when Specification_F_Package_Declaration => return Specification_F_Package_Declaration (N_Bare_Specification);
when others => null;
end case;
end;
when Rflx_State_Range =>
declare
N_Bare_State : constant Bare_State := Node;
begin
case Field is
when State_F_Identifier => return State_F_Identifier (N_Bare_State);
when State_F_Description => return State_F_Description (N_Bare_State);
when State_F_Body => return State_F_Body (N_Bare_State);
when others => null;
end case;
end;
when Rflx_State_Body_Range =>
declare
N_Bare_State_Body : constant Bare_State_Body := Node;
begin
case Field is
when State_Body_F_Declarations => return State_Body_F_Declarations (N_Bare_State_Body);
when State_Body_F_Actions => return State_Body_F_Actions (N_Bare_State_Body);
when State_Body_F_Conditional_Transitions => return State_Body_F_Conditional_Transitions (N_Bare_State_Body);
when State_Body_F_Final_Transition => return State_Body_F_Final_Transition (N_Bare_State_Body);
when State_Body_F_Exception_Transition => return State_Body_F_Exception_Transition (N_Bare_State_Body);
when State_Body_F_End_Identifier => return State_Body_F_End_Identifier (N_Bare_State_Body);
when others => null;
end case;
end;
when Rflx_Assignment_Range =>
declare
N_Bare_Assignment : constant Bare_Assignment := Node;
begin
case Field is
when Assignment_F_Identifier => return Assignment_F_Identifier (N_Bare_Assignment);
when Assignment_F_Expression => return Assignment_F_Expression (N_Bare_Assignment);
when others => null;
end case;
end;
when Rflx_Attribute_Statement_Range =>
declare
N_Bare_Attribute_Statement : constant Bare_Attribute_Statement := Node;
begin
case Field is
when Attribute_Statement_F_Identifier => return Attribute_Statement_F_Identifier (N_Bare_Attribute_Statement);
when Attribute_Statement_F_Attr => return Attribute_Statement_F_Attr (N_Bare_Attribute_Statement);
when Attribute_Statement_F_Expression => return Attribute_Statement_F_Expression (N_Bare_Attribute_Statement);
when others => null;
end case;
end;
when Rflx_Message_Field_Assignment_Range =>
declare
N_Bare_Message_Field_Assignment : constant Bare_Message_Field_Assignment := Node;
begin
case Field is
when Message_Field_Assignment_F_Message => return Message_Field_Assignment_F_Message (N_Bare_Message_Field_Assignment);
when Message_Field_Assignment_F_Field => return Message_Field_Assignment_F_Field (N_Bare_Message_Field_Assignment);
when Message_Field_Assignment_F_Expression => return Message_Field_Assignment_F_Expression (N_Bare_Message_Field_Assignment);
when others => null;
end case;
end;
when Rflx_Reset_Range =>
declare
N_Bare_Reset : constant Bare_Reset := Node;
begin
case Field is
when Reset_F_Identifier => return Reset_F_Identifier (N_Bare_Reset);
when Reset_F_Associations => return Reset_F_Associations (N_Bare_Reset);
when others => null;
end case;
end;
when Rflx_Term_Assoc_Range =>
declare
N_Bare_Term_Assoc : constant Bare_Term_Assoc := Node;
begin
case Field is
when Term_Assoc_F_Identifier => return Term_Assoc_F_Identifier (N_Bare_Term_Assoc);
when Term_Assoc_F_Expression => return Term_Assoc_F_Expression (N_Bare_Term_Assoc);
when others => null;
end case;
end;
when Rflx_Then_Node_Range =>
declare
N_Bare_Then_Node : constant Bare_Then_Node := Node;
begin
case Field is
when Then_Node_F_Target => return Then_Node_F_Target (N_Bare_Then_Node);
when Then_Node_F_Aspects => return Then_Node_F_Aspects (N_Bare_Then_Node);
when Then_Node_F_Condition => return Then_Node_F_Condition (N_Bare_Then_Node);
when others => null;
end case;
end;
when Rflx_Transition_Range =>
declare
N_Bare_Transition : constant Bare_Transition := Node;
begin
case Field is
when Transition_F_Target => return Transition_F_Target (N_Bare_Transition);
when Transition_F_Description => return Transition_F_Description (N_Bare_Transition);
when others => null;
end case;
case Rflx_Transition_Range (Kind) is
when Rflx_Conditional_Transition_Range =>
declare
N_Bare_Conditional_Transition : constant Bare_Conditional_Transition := N_Bare_Transition;
begin
case Field is
when Conditional_Transition_F_Condition => return Conditional_Transition_F_Condition (N_Bare_Conditional_Transition);
when others => null;
end case;
end;
when others => null;
end case;
end;
when Rflx_Type_Argument_Range =>
declare
N_Bare_Type_Argument : constant Bare_Type_Argument := Node;
begin
case Field is
when Type_Argument_F_Identifier => return Type_Argument_F_Identifier (N_Bare_Type_Argument);
when Type_Argument_F_Expression => return Type_Argument_F_Expression (N_Bare_Type_Argument);
when others => null;
end case;
end;
when Rflx_Message_Type_Def_Range =>
declare
N_Bare_Message_Type_Def : constant Bare_Message_Type_Def := Node;
begin
case Field is
when Message_Type_Def_F_Message_Fields => return Message_Type_Def_F_Message_Fields (N_Bare_Message_Type_Def);
when Message_Type_Def_F_Aspects => return Message_Type_Def_F_Aspects (N_Bare_Message_Type_Def);
when others => null;
end case;
end;
when Rflx_Named_Enumeration_Def_Range =>
declare
N_Bare_Named_Enumeration_Def : constant Bare_Named_Enumeration_Def := Node;
begin
case Field is
when Named_Enumeration_Def_F_Elements => return Named_Enumeration_Def_F_Elements (N_Bare_Named_Enumeration_Def);
when others => null;
end case;
end;
when Rflx_Positional_Enumeration_Def_Range =>
declare
N_Bare_Positional_Enumeration_Def : constant Bare_Positional_Enumeration_Def := Node;
begin
case Field is
when Positional_Enumeration_Def_F_Elements => return Positional_Enumeration_Def_F_Elements (N_Bare_Positional_Enumeration_Def);
when others => null;
end case;
end;
when Rflx_Enumeration_Type_Def_Range =>
declare
N_Bare_Enumeration_Type_Def : constant Bare_Enumeration_Type_Def := Node;
begin
case Field is
when Enumeration_Type_Def_F_Elements => return Enumeration_Type_Def_F_Elements (N_Bare_Enumeration_Type_Def);
when Enumeration_Type_Def_F_Aspects => return Enumeration_Type_Def_F_Aspects (N_Bare_Enumeration_Type_Def);
when others => null;
end case;
end;
when Rflx_Modular_Type_Def_Range =>
declare
N_Bare_Modular_Type_Def : constant Bare_Modular_Type_Def := Node;
begin
case Field is
when Modular_Type_Def_F_Mod => return Modular_Type_Def_F_Mod (N_Bare_Modular_Type_Def);
when others => null;
end case;
end;
when Rflx_Range_Type_Def_Range =>
declare
N_Bare_Range_Type_Def : constant Bare_Range_Type_Def := Node;
begin
case Field is
when Range_Type_Def_F_First => return Range_Type_Def_F_First (N_Bare_Range_Type_Def);
when Range_Type_Def_F_Last => return Range_Type_Def_F_Last (N_Bare_Range_Type_Def);
when Range_Type_Def_F_Size => return Range_Type_Def_F_Size (N_Bare_Range_Type_Def);
when others => null;
end case;
end;
when Rflx_Sequence_Type_Def_Range =>
declare
N_Bare_Sequence_Type_Def : constant Bare_Sequence_Type_Def := Node;
begin
case Field is
when Sequence_Type_Def_F_Element_Type => return Sequence_Type_Def_F_Element_Type (N_Bare_Sequence_Type_Def);
when others => null;
end case;
end;
when Rflx_Type_Derivation_Def_Range =>
declare
N_Bare_Type_Derivation_Def : constant Bare_Type_Derivation_Def := Node;
begin
case Field is
when Type_Derivation_Def_F_Base => return Type_Derivation_Def_F_Base (N_Bare_Type_Derivation_Def);
when others => null;
end case;
end;
when others => null;
end case;

      return (raise Bad_Type_Error with "no such field on this node");
   end Eval_Syntax_Field;

   -----------
   -- Index --
   -----------

   function Index
     (Kind : R_F_L_X_Node_Kind_Type; Field : Syntax_Field_Reference) return Positive is
   begin
         
         case Kind is
               when Rflx_I_D =>
               return (case Field is
                       when I_D_F_Package => 1,
                       when I_D_F_Name => 2,
                       when others => raise Bad_Type_Error);
               when Rflx_Unqualified_I_D =>
               return (case Field is
                       when others => raise Bad_Type_Error);
               when Rflx_Aspect =>
               return (case Field is
                       when Aspect_F_Identifier => 1,
                       when Aspect_F_Value => 2,
                       when others => raise Bad_Type_Error);
               when Rflx_Attr_First =>
               return (case Field is
                       when others => raise Bad_Type_Error);
               when Rflx_Attr_Has_Data =>
               return (case Field is
                       when others => raise Bad_Type_Error);
               when Rflx_Attr_Head =>
               return (case Field is
                       when others => raise Bad_Type_Error);
               when Rflx_Attr_Last =>
               return (case Field is
                       when others => raise Bad_Type_Error);
               when Rflx_Attr_Opaque =>
               return (case Field is
                       when others => raise Bad_Type_Error);
               when Rflx_Attr_Present =>
               return (case Field is
                       when others => raise Bad_Type_Error);
               when Rflx_Attr_Size =>
               return (case Field is
                       when others => raise Bad_Type_Error);
               when Rflx_Attr_Valid =>
               return (case Field is
                       when others => raise Bad_Type_Error);
               when Rflx_Attr_Valid_Checksum =>
               return (case Field is
                       when others => raise Bad_Type_Error);
               when Rflx_Attr_Stmt_Append =>
               return (case Field is
                       when others => raise Bad_Type_Error);
               when Rflx_Attr_Stmt_Extend =>
               return (case Field is
                       when others => raise Bad_Type_Error);
               when Rflx_Attr_Stmt_Read =>
               return (case Field is
                       when others => raise Bad_Type_Error);
               when Rflx_Attr_Stmt_Write =>
               return (case Field is
                       when others => raise Bad_Type_Error);
               when Rflx_Message_Aggregate_Associations =>
               return (case Field is
                       when Message_Aggregate_Associations_F_Associations => 1,
                       when others => raise Bad_Type_Error);
               when Rflx_Null_Message_Aggregate =>
               return (case Field is
                       when others => raise Bad_Type_Error);
               when Rflx_Checksum_Val =>
               return (case Field is
                       when Checksum_Val_F_Data => 1,
                       when others => raise Bad_Type_Error);
               when Rflx_Checksum_Value_Range =>
               return (case Field is
                       when Checksum_Value_Range_F_First => 1,
                       when Checksum_Value_Range_F_Last => 2,
                       when others => raise Bad_Type_Error);
               when Rflx_Byte_Order_Type_Highorderfirst =>
               return (case Field is
                       when others => raise Bad_Type_Error);
               when Rflx_Byte_Order_Type_Loworderfirst =>
               return (case Field is
                       when others => raise Bad_Type_Error);
               when Rflx_Readable =>
               return (case Field is
                       when others => raise Bad_Type_Error);
               when Rflx_Writable =>
               return (case Field is
                       when others => raise Bad_Type_Error);
               when Rflx_Checksum_Assoc =>
               return (case Field is
                       when Checksum_Assoc_F_Identifier => 1,
                       when Checksum_Assoc_F_Covered_Fields => 2,
                       when others => raise Bad_Type_Error);
               when Rflx_Refinement_Decl =>
               return (case Field is
                       when Refinement_Decl_F_Pdu => 1,
                       when Refinement_Decl_F_Field => 2,
                       when Refinement_Decl_F_Sdu => 3,
                       when Refinement_Decl_F_Condition => 4,
                       when others => raise Bad_Type_Error);
               when Rflx_Session_Decl =>
               return (case Field is
                       when Session_Decl_F_Parameters => 1,
                       when Session_Decl_F_Identifier => 2,
                       when Session_Decl_F_Declarations => 3,
                       when Session_Decl_F_States => 4,
                       when Session_Decl_F_End_Identifier => 5,
                       when others => raise Bad_Type_Error);
               when Rflx_Type_Decl =>
               return (case Field is
                       when Type_Decl_F_Identifier => 1,
                       when Type_Decl_F_Parameters => 2,
                       when Type_Decl_F_Definition => 3,
                       when others => raise Bad_Type_Error);
               when Rflx_Description =>
               return (case Field is
                       when Description_F_Content => 1,
                       when others => raise Bad_Type_Error);
               when Rflx_Element_Value_Assoc =>
               return (case Field is
                       when Element_Value_Assoc_F_Identifier => 1,
                       when Element_Value_Assoc_F_Literal => 2,
                       when others => raise Bad_Type_Error);
               when Rflx_Attribute =>
               return (case Field is
                       when Attribute_F_Expression => 1,
                       when Attribute_F_Kind => 2,
                       when others => raise Bad_Type_Error);
               when Rflx_Bin_Op =>
               return (case Field is
                       when Bin_Op_F_Left => 1,
                       when Bin_Op_F_Op => 2,
                       when Bin_Op_F_Right => 3,
                       when others => raise Bad_Type_Error);
               when Rflx_Binding =>
               return (case Field is
                       when Binding_F_Expression => 1,
                       when Binding_F_Bindings => 2,
                       when others => raise Bad_Type_Error);
               when Rflx_Call =>
               return (case Field is
                       when Call_F_Identifier => 1,
                       when Call_F_Arguments => 2,
                       when others => raise Bad_Type_Error);
               when Rflx_Case_Expression =>
               return (case Field is
                       when Case_Expression_F_Expression => 1,
                       when Case_Expression_F_Choices => 2,
                       when others => raise Bad_Type_Error);
               when Rflx_Choice =>
               return (case Field is
                       when Choice_F_Selectors => 1,
                       when Choice_F_Expression => 2,
                       when others => raise Bad_Type_Error);
               when Rflx_Comprehension =>
               return (case Field is
                       when Comprehension_F_Iterator => 1,
                       when Comprehension_F_Sequence => 2,
                       when Comprehension_F_Condition => 3,
                       when Comprehension_F_Selector => 4,
                       when others => raise Bad_Type_Error);
               when Rflx_Context_Item =>
               return (case Field is
                       when Context_Item_F_Item => 1,
                       when others => raise Bad_Type_Error);
               when Rflx_Conversion =>
               return (case Field is
                       when Conversion_F_Target_Identifier => 1,
                       when Conversion_F_Argument => 2,
                       when others => raise Bad_Type_Error);
               when Rflx_Message_Aggregate =>
               return (case Field is
                       when Message_Aggregate_F_Identifier => 1,
                       when Message_Aggregate_F_Values => 2,
                       when others => raise Bad_Type_Error);
               when Rflx_Negation =>
               return (case Field is
                       when Negation_F_Data => 1,
                       when others => raise Bad_Type_Error);
               when Rflx_Numeric_Literal =>
               return (case Field is
                       when others => raise Bad_Type_Error);
               when Rflx_Paren_Expression =>
               return (case Field is
                       when Paren_Expression_F_Data => 1,
                       when others => raise Bad_Type_Error);
               when Rflx_Quantified_Expression =>
               return (case Field is
                       when Quantified_Expression_F_Operation => 1,
                       when Quantified_Expression_F_Parameter_Identifier => 2,
                       when Quantified_Expression_F_Iterable => 3,
                       when Quantified_Expression_F_Predicate => 4,
                       when others => raise Bad_Type_Error);
               when Rflx_Select_Node =>
               return (case Field is
                       when Select_Node_F_Expression => 1,
                       when Select_Node_F_Selector => 2,
                       when others => raise Bad_Type_Error);
               when Rflx_Concatenation =>
               return (case Field is
                       when Concatenation_F_Left => 1,
                       when Concatenation_F_Right => 2,
                       when others => raise Bad_Type_Error);
               when Rflx_Sequence_Aggregate =>
               return (case Field is
                       when Sequence_Aggregate_F_Values => 1,
                       when others => raise Bad_Type_Error);
               when Rflx_String_Literal =>
               return (case Field is
                       when others => raise Bad_Type_Error);
               when Rflx_Variable =>
               return (case Field is
                       when Variable_F_Identifier => 1,
                       when others => raise Bad_Type_Error);
               when Rflx_Formal_Channel_Decl =>
               return (case Field is
                       when Formal_Channel_Decl_F_Identifier => 1,
                       when Formal_Channel_Decl_F_Parameters => 2,
                       when others => raise Bad_Type_Error);
               when Rflx_Formal_Function_Decl =>
               return (case Field is
                       when Formal_Function_Decl_F_Identifier => 1,
                       when Formal_Function_Decl_F_Parameters => 2,
                       when Formal_Function_Decl_F_Return_Type_Identifier => 3,
                       when others => raise Bad_Type_Error);
               when Rflx_Renaming_Decl =>
               return (case Field is
                       when Renaming_Decl_F_Identifier => 1,
                       when Renaming_Decl_F_Type_Identifier => 2,
                       when Renaming_Decl_F_Expression => 3,
                       when others => raise Bad_Type_Error);
               when Rflx_Variable_Decl =>
               return (case Field is
                       when Variable_Decl_F_Identifier => 1,
                       when Variable_Decl_F_Type_Identifier => 2,
                       when Variable_Decl_F_Initializer => 3,
                       when others => raise Bad_Type_Error);
               when Rflx_Message_Aggregate_Association =>
               return (case Field is
                       when Message_Aggregate_Association_F_Identifier => 1,
                       when Message_Aggregate_Association_F_Expression => 2,
                       when others => raise Bad_Type_Error);
               when Rflx_Byte_Order_Aspect =>
               return (case Field is
                       when Byte_Order_Aspect_F_Byte_Order => 1,
                       when others => raise Bad_Type_Error);
               when Rflx_Checksum_Aspect =>
               return (case Field is
                       when Checksum_Aspect_F_Associations => 1,
                       when others => raise Bad_Type_Error);
               when Rflx_Message_Field =>
               return (case Field is
                       when Message_Field_F_Identifier => 1,
                       when Message_Field_F_Type_Identifier => 2,
                       when Message_Field_F_Type_Arguments => 3,
                       when Message_Field_F_Aspects => 4,
                       when Message_Field_F_Condition => 5,
                       when Message_Field_F_Thens => 6,
                       when others => raise Bad_Type_Error);
               when Rflx_Message_Fields =>
               return (case Field is
                       when Message_Fields_F_Initial_Field => 1,
                       when Message_Fields_F_Fields => 2,
                       when others => raise Bad_Type_Error);
               when Rflx_Null_Message_Field =>
               return (case Field is
                       when Null_Message_Field_F_Then => 1,
                       when others => raise Bad_Type_Error);
               when Rflx_Op_Add =>
               return (case Field is
                       when others => raise Bad_Type_Error);
               when Rflx_Op_And =>
               return (case Field is
                       when others => raise Bad_Type_Error);
               when Rflx_Op_Div =>
               return (case Field is
                       when others => raise Bad_Type_Error);
               when Rflx_Op_Eq =>
               return (case Field is
                       when others => raise Bad_Type_Error);
               when Rflx_Op_Ge =>
               return (case Field is
                       when others => raise Bad_Type_Error);
               when Rflx_Op_Gt =>
               return (case Field is
                       when others => raise Bad_Type_Error);
               when Rflx_Op_In =>
               return (case Field is
                       when others => raise Bad_Type_Error);
               when Rflx_Op_Le =>
               return (case Field is
                       when others => raise Bad_Type_Error);
               when Rflx_Op_Lt =>
               return (case Field is
                       when others => raise Bad_Type_Error);
               when Rflx_Op_Mod =>
               return (case Field is
                       when others => raise Bad_Type_Error);
               when Rflx_Op_Mul =>
               return (case Field is
                       when others => raise Bad_Type_Error);
               when Rflx_Op_Neq =>
               return (case Field is
                       when others => raise Bad_Type_Error);
               when Rflx_Op_Notin =>
               return (case Field is
                       when others => raise Bad_Type_Error);
               when Rflx_Op_Or =>
               return (case Field is
                       when others => raise Bad_Type_Error);
               when Rflx_Op_Pow =>
               return (case Field is
                       when others => raise Bad_Type_Error);
               when Rflx_Op_Sub =>
               return (case Field is
                       when others => raise Bad_Type_Error);
               when Rflx_Package_Node =>
               return (case Field is
                       when Package_Node_F_Identifier => 1,
                       when Package_Node_F_Declarations => 2,
                       when Package_Node_F_End_Identifier => 3,
                       when others => raise Bad_Type_Error);
               when Rflx_Parameter =>
               return (case Field is
                       when Parameter_F_Identifier => 1,
                       when Parameter_F_Type_Identifier => 2,
                       when others => raise Bad_Type_Error);
               when Rflx_Parameters =>
               return (case Field is
                       when Parameters_F_Parameters => 1,
                       when others => raise Bad_Type_Error);
               when Rflx_Quantifier_All =>
               return (case Field is
                       when others => raise Bad_Type_Error);
               when Rflx_Quantifier_Some =>
               return (case Field is
                       when others => raise Bad_Type_Error);
               when Rflx_Aspect_List =>
               return (case Field is
                       when others => raise Bad_Type_Error);
               when Rflx_Base_Checksum_Val_List =>
               return (case Field is
                       when others => raise Bad_Type_Error);
               when Rflx_Channel_Attribute_List =>
               return (case Field is
                       when others => raise Bad_Type_Error);
               when Rflx_Checksum_Assoc_List =>
               return (case Field is
                       when others => raise Bad_Type_Error);
               when Rflx_Choice_List =>
               return (case Field is
                       when others => raise Bad_Type_Error);
               when Rflx_Conditional_Transition_List =>
               return (case Field is
                       when others => raise Bad_Type_Error);
               when Rflx_Context_Item_List =>
               return (case Field is
                       when others => raise Bad_Type_Error);
               when Rflx_Declaration_List =>
               return (case Field is
                       when others => raise Bad_Type_Error);
               when Rflx_Element_Value_Assoc_List =>
               return (case Field is
                       when others => raise Bad_Type_Error);
               when Rflx_Expr_List =>
               return (case Field is
                       when others => raise Bad_Type_Error);
               when Rflx_Formal_Decl_List =>
               return (case Field is
                       when others => raise Bad_Type_Error);
               when Rflx_Local_Decl_List =>
               return (case Field is
                       when others => raise Bad_Type_Error);
               when Rflx_Message_Aggregate_Association_List =>
               return (case Field is
                       when others => raise Bad_Type_Error);
               when Rflx_Message_Aspect_List =>
               return (case Field is
                       when others => raise Bad_Type_Error);
               when Rflx_Message_Field_List =>
               return (case Field is
                       when others => raise Bad_Type_Error);
               when Rflx_Numeric_Literal_List =>
               return (case Field is
                       when others => raise Bad_Type_Error);
               when Rflx_Parameter_List =>
               return (case Field is
                       when others => raise Bad_Type_Error);
               when Rflx_R_F_L_X_Node_List =>
               return (case Field is
                       when others => raise Bad_Type_Error);
               when Rflx_State_List =>
               return (case Field is
                       when others => raise Bad_Type_Error);
               when Rflx_Statement_List =>
               return (case Field is
                       when others => raise Bad_Type_Error);
               when Rflx_Term_Assoc_List =>
               return (case Field is
                       when others => raise Bad_Type_Error);
               when Rflx_Then_Node_List =>
               return (case Field is
                       when others => raise Bad_Type_Error);
               when Rflx_Type_Argument_List =>
               return (case Field is
                       when others => raise Bad_Type_Error);
               when Rflx_Unqualified_I_D_List =>
               return (case Field is
                       when others => raise Bad_Type_Error);
               when Rflx_Specification =>
               return (case Field is
                       when Specification_F_Context_Clause => 1,
                       when Specification_F_Package_Declaration => 2,
                       when others => raise Bad_Type_Error);
               when Rflx_State =>
               return (case Field is
                       when State_F_Identifier => 1,
                       when State_F_Description => 2,
                       when State_F_Body => 3,
                       when others => raise Bad_Type_Error);
               when Rflx_State_Body =>
               return (case Field is
                       when State_Body_F_Declarations => 1,
                       when State_Body_F_Actions => 2,
                       when State_Body_F_Conditional_Transitions => 3,
                       when State_Body_F_Final_Transition => 4,
                       when State_Body_F_Exception_Transition => 5,
                       when State_Body_F_End_Identifier => 6,
                       when others => raise Bad_Type_Error);
               when Rflx_Assignment =>
               return (case Field is
                       when Assignment_F_Identifier => 1,
                       when Assignment_F_Expression => 2,
                       when others => raise Bad_Type_Error);
               when Rflx_Attribute_Statement =>
               return (case Field is
                       when Attribute_Statement_F_Identifier => 1,
                       when Attribute_Statement_F_Attr => 2,
                       when Attribute_Statement_F_Expression => 3,
                       when others => raise Bad_Type_Error);
               when Rflx_Message_Field_Assignment =>
               return (case Field is
                       when Message_Field_Assignment_F_Message => 1,
                       when Message_Field_Assignment_F_Field => 2,
                       when Message_Field_Assignment_F_Expression => 3,
                       when others => raise Bad_Type_Error);
               when Rflx_Reset =>
               return (case Field is
                       when Reset_F_Identifier => 1,
                       when Reset_F_Associations => 2,
                       when others => raise Bad_Type_Error);
               when Rflx_Term_Assoc =>
               return (case Field is
                       when Term_Assoc_F_Identifier => 1,
                       when Term_Assoc_F_Expression => 2,
                       when others => raise Bad_Type_Error);
               when Rflx_Then_Node =>
               return (case Field is
                       when Then_Node_F_Target => 1,
                       when Then_Node_F_Aspects => 2,
                       when Then_Node_F_Condition => 3,
                       when others => raise Bad_Type_Error);
               when Rflx_Transition =>
               return (case Field is
                       when Transition_F_Target => 1,
                       when Transition_F_Description => 2,
                       when others => raise Bad_Type_Error);
               when Rflx_Conditional_Transition =>
               return (case Field is
                       when Transition_F_Target => 1,
                       when Transition_F_Description => 2,
                       when Conditional_Transition_F_Condition => 3,
                       when others => raise Bad_Type_Error);
               when Rflx_Type_Argument =>
               return (case Field is
                       when Type_Argument_F_Identifier => 1,
                       when Type_Argument_F_Expression => 2,
                       when others => raise Bad_Type_Error);
               when Rflx_Message_Type_Def =>
               return (case Field is
                       when Message_Type_Def_F_Message_Fields => 1,
                       when Message_Type_Def_F_Aspects => 2,
                       when others => raise Bad_Type_Error);
               when Rflx_Null_Message_Type_Def =>
               return (case Field is
                       when others => raise Bad_Type_Error);
               when Rflx_Named_Enumeration_Def =>
               return (case Field is
                       when Named_Enumeration_Def_F_Elements => 1,
                       when others => raise Bad_Type_Error);
               when Rflx_Positional_Enumeration_Def =>
               return (case Field is
                       when Positional_Enumeration_Def_F_Elements => 1,
                       when others => raise Bad_Type_Error);
               when Rflx_Enumeration_Type_Def =>
               return (case Field is
                       when Enumeration_Type_Def_F_Elements => 1,
                       when Enumeration_Type_Def_F_Aspects => 2,
                       when others => raise Bad_Type_Error);
               when Rflx_Modular_Type_Def =>
               return (case Field is
                       when Modular_Type_Def_F_Mod => 1,
                       when others => raise Bad_Type_Error);
               when Rflx_Range_Type_Def =>
               return (case Field is
                       when Range_Type_Def_F_First => 1,
                       when Range_Type_Def_F_Last => 2,
                       when Range_Type_Def_F_Size => 3,
                       when others => raise Bad_Type_Error);
               when Rflx_Sequence_Type_Def =>
               return (case Field is
                       when Sequence_Type_Def_F_Element_Type => 1,
                       when others => raise Bad_Type_Error);
               when Rflx_Type_Derivation_Def =>
               return (case Field is
                       when Type_Derivation_Def_F_Base => 1,
                       when others => raise Bad_Type_Error);
         end case;

   end Index;

   ---------------------------------------
   -- Syntax_Field_Reference_From_Index --
   ---------------------------------------

   function Syntax_Field_Reference_From_Index
     (Kind : R_F_L_X_Node_Kind_Type; Index : Positive) return Syntax_Field_Reference is
   begin
      
      case Rflx_R_F_L_X_Node (Kind) is
when Rflx_I_D_Range =>
case Index is
when 1 => return I_D_F_Package;
when 2 => return I_D_F_Name;
when others => null;
end case;
when Rflx_Aspect_Range =>
case Index is
when 1 => return Aspect_F_Identifier;
when 2 => return Aspect_F_Value;
when others => null;
end case;
when Rflx_Message_Aggregate_Associations_Range =>
case Index is
when 1 => return Message_Aggregate_Associations_F_Associations;
when others => null;
end case;
when Rflx_Checksum_Val_Range =>
case Index is
when 1 => return Checksum_Val_F_Data;
when others => null;
end case;
when Rflx_Checksum_Value_Range_Range =>
case Index is
when 1 => return Checksum_Value_Range_F_First;
when 2 => return Checksum_Value_Range_F_Last;
when others => null;
end case;
when Rflx_Checksum_Assoc_Range =>
case Index is
when 1 => return Checksum_Assoc_F_Identifier;
when 2 => return Checksum_Assoc_F_Covered_Fields;
when others => null;
end case;
when Rflx_Refinement_Decl_Range =>
case Index is
when 1 => return Refinement_Decl_F_Pdu;
when 2 => return Refinement_Decl_F_Field;
when 3 => return Refinement_Decl_F_Sdu;
when 4 => return Refinement_Decl_F_Condition;
when others => null;
end case;
when Rflx_Session_Decl_Range =>
case Index is
when 1 => return Session_Decl_F_Parameters;
when 2 => return Session_Decl_F_Identifier;
when 3 => return Session_Decl_F_Declarations;
when 4 => return Session_Decl_F_States;
when 5 => return Session_Decl_F_End_Identifier;
when others => null;
end case;
when Rflx_Type_Decl_Range =>
case Index is
when 1 => return Type_Decl_F_Identifier;
when 2 => return Type_Decl_F_Parameters;
when 3 => return Type_Decl_F_Definition;
when others => null;
end case;
when Rflx_Description_Range =>
case Index is
when 1 => return Description_F_Content;
when others => null;
end case;
when Rflx_Element_Value_Assoc_Range =>
case Index is
when 1 => return Element_Value_Assoc_F_Identifier;
when 2 => return Element_Value_Assoc_F_Literal;
when others => null;
end case;
when Rflx_Attribute_Range =>
case Index is
when 1 => return Attribute_F_Expression;
when 2 => return Attribute_F_Kind;
when others => null;
end case;
when Rflx_Bin_Op_Range =>
case Index is
when 1 => return Bin_Op_F_Left;
when 2 => return Bin_Op_F_Op;
when 3 => return Bin_Op_F_Right;
when others => null;
end case;
when Rflx_Binding_Range =>
case Index is
when 1 => return Binding_F_Expression;
when 2 => return Binding_F_Bindings;
when others => null;
end case;
when Rflx_Call_Range =>
case Index is
when 1 => return Call_F_Identifier;
when 2 => return Call_F_Arguments;
when others => null;
end case;
when Rflx_Case_Expression_Range =>
case Index is
when 1 => return Case_Expression_F_Expression;
when 2 => return Case_Expression_F_Choices;
when others => null;
end case;
when Rflx_Choice_Range =>
case Index is
when 1 => return Choice_F_Selectors;
when 2 => return Choice_F_Expression;
when others => null;
end case;
when Rflx_Comprehension_Range =>
case Index is
when 1 => return Comprehension_F_Iterator;
when 2 => return Comprehension_F_Sequence;
when 3 => return Comprehension_F_Condition;
when 4 => return Comprehension_F_Selector;
when others => null;
end case;
when Rflx_Context_Item_Range =>
case Index is
when 1 => return Context_Item_F_Item;
when others => null;
end case;
when Rflx_Conversion_Range =>
case Index is
when 1 => return Conversion_F_Target_Identifier;
when 2 => return Conversion_F_Argument;
when others => null;
end case;
when Rflx_Message_Aggregate_Range =>
case Index is
when 1 => return Message_Aggregate_F_Identifier;
when 2 => return Message_Aggregate_F_Values;
when others => null;
end case;
when Rflx_Negation_Range =>
case Index is
when 1 => return Negation_F_Data;
when others => null;
end case;
when Rflx_Paren_Expression_Range =>
case Index is
when 1 => return Paren_Expression_F_Data;
when others => null;
end case;
when Rflx_Quantified_Expression_Range =>
case Index is
when 1 => return Quantified_Expression_F_Operation;
when 2 => return Quantified_Expression_F_Parameter_Identifier;
when 3 => return Quantified_Expression_F_Iterable;
when 4 => return Quantified_Expression_F_Predicate;
when others => null;
end case;
when Rflx_Select_Node_Range =>
case Index is
when 1 => return Select_Node_F_Expression;
when 2 => return Select_Node_F_Selector;
when others => null;
end case;
when Rflx_Concatenation_Range =>
case Index is
when 1 => return Concatenation_F_Left;
when 2 => return Concatenation_F_Right;
when others => null;
end case;
when Rflx_Sequence_Aggregate_Range =>
case Index is
when 1 => return Sequence_Aggregate_F_Values;
when others => null;
end case;
when Rflx_Variable_Range =>
case Index is
when 1 => return Variable_F_Identifier;
when others => null;
end case;
when Rflx_Formal_Channel_Decl_Range =>
case Index is
when 1 => return Formal_Channel_Decl_F_Identifier;
when 2 => return Formal_Channel_Decl_F_Parameters;
when others => null;
end case;
when Rflx_Formal_Function_Decl_Range =>
case Index is
when 1 => return Formal_Function_Decl_F_Identifier;
when 2 => return Formal_Function_Decl_F_Parameters;
when 3 => return Formal_Function_Decl_F_Return_Type_Identifier;
when others => null;
end case;
when Rflx_Renaming_Decl_Range =>
case Index is
when 1 => return Renaming_Decl_F_Identifier;
when 2 => return Renaming_Decl_F_Type_Identifier;
when 3 => return Renaming_Decl_F_Expression;
when others => null;
end case;
when Rflx_Variable_Decl_Range =>
case Index is
when 1 => return Variable_Decl_F_Identifier;
when 2 => return Variable_Decl_F_Type_Identifier;
when 3 => return Variable_Decl_F_Initializer;
when others => null;
end case;
when Rflx_Message_Aggregate_Association_Range =>
case Index is
when 1 => return Message_Aggregate_Association_F_Identifier;
when 2 => return Message_Aggregate_Association_F_Expression;
when others => null;
end case;
when Rflx_Byte_Order_Aspect_Range =>
case Index is
when 1 => return Byte_Order_Aspect_F_Byte_Order;
when others => null;
end case;
when Rflx_Checksum_Aspect_Range =>
case Index is
when 1 => return Checksum_Aspect_F_Associations;
when others => null;
end case;
when Rflx_Message_Field_Range =>
case Index is
when 1 => return Message_Field_F_Identifier;
when 2 => return Message_Field_F_Type_Identifier;
when 3 => return Message_Field_F_Type_Arguments;
when 4 => return Message_Field_F_Aspects;
when 5 => return Message_Field_F_Condition;
when 6 => return Message_Field_F_Thens;
when others => null;
end case;
when Rflx_Message_Fields_Range =>
case Index is
when 1 => return Message_Fields_F_Initial_Field;
when 2 => return Message_Fields_F_Fields;
when others => null;
end case;
when Rflx_Null_Message_Field_Range =>
case Index is
when 1 => return Null_Message_Field_F_Then;
when others => null;
end case;
when Rflx_Package_Node_Range =>
case Index is
when 1 => return Package_Node_F_Identifier;
when 2 => return Package_Node_F_Declarations;
when 3 => return Package_Node_F_End_Identifier;
when others => null;
end case;
when Rflx_Parameter_Range =>
case Index is
when 1 => return Parameter_F_Identifier;
when 2 => return Parameter_F_Type_Identifier;
when others => null;
end case;
when Rflx_Parameters_Range =>
case Index is
when 1 => return Parameters_F_Parameters;
when others => null;
end case;
when Rflx_R_F_L_X_Node_Base_List =>
raise Bad_Type_Error with "List AST nodes have no field";
when Rflx_Specification_Range =>
case Index is
when 1 => return Specification_F_Context_Clause;
when 2 => return Specification_F_Package_Declaration;
when others => null;
end case;
when Rflx_State_Range =>
case Index is
when 1 => return State_F_Identifier;
when 2 => return State_F_Description;
when 3 => return State_F_Body;
when others => null;
end case;
when Rflx_State_Body_Range =>
case Index is
when 1 => return State_Body_F_Declarations;
when 2 => return State_Body_F_Actions;
when 3 => return State_Body_F_Conditional_Transitions;
when 4 => return State_Body_F_Final_Transition;
when 5 => return State_Body_F_Exception_Transition;
when 6 => return State_Body_F_End_Identifier;
when others => null;
end case;
when Rflx_Assignment_Range =>
case Index is
when 1 => return Assignment_F_Identifier;
when 2 => return Assignment_F_Expression;
when others => null;
end case;
when Rflx_Attribute_Statement_Range =>
case Index is
when 1 => return Attribute_Statement_F_Identifier;
when 2 => return Attribute_Statement_F_Attr;
when 3 => return Attribute_Statement_F_Expression;
when others => null;
end case;
when Rflx_Message_Field_Assignment_Range =>
case Index is
when 1 => return Message_Field_Assignment_F_Message;
when 2 => return Message_Field_Assignment_F_Field;
when 3 => return Message_Field_Assignment_F_Expression;
when others => null;
end case;
when Rflx_Reset_Range =>
case Index is
when 1 => return Reset_F_Identifier;
when 2 => return Reset_F_Associations;
when others => null;
end case;
when Rflx_Term_Assoc_Range =>
case Index is
when 1 => return Term_Assoc_F_Identifier;
when 2 => return Term_Assoc_F_Expression;
when others => null;
end case;
when Rflx_Then_Node_Range =>
case Index is
when 1 => return Then_Node_F_Target;
when 2 => return Then_Node_F_Aspects;
when 3 => return Then_Node_F_Condition;
when others => null;
end case;
when Rflx_Transition_Range =>
case Index is
when 1 => return Transition_F_Target;
when 2 => return Transition_F_Description;
when others => null;
end case;
case Rflx_Transition_Range (Kind) is
when Rflx_Conditional_Transition_Range =>
case Index is
when 3 => return Conditional_Transition_F_Condition;
when others => null;
end case;
when others => null;
end case;
when Rflx_Type_Argument_Range =>
case Index is
when 1 => return Type_Argument_F_Identifier;
when 2 => return Type_Argument_F_Expression;
when others => null;
end case;
when Rflx_Message_Type_Def_Range =>
case Index is
when 1 => return Message_Type_Def_F_Message_Fields;
when 2 => return Message_Type_Def_F_Aspects;
when others => null;
end case;
when Rflx_Named_Enumeration_Def_Range =>
case Index is
when 1 => return Named_Enumeration_Def_F_Elements;
when others => null;
end case;
when Rflx_Positional_Enumeration_Def_Range =>
case Index is
when 1 => return Positional_Enumeration_Def_F_Elements;
when others => null;
end case;
when Rflx_Enumeration_Type_Def_Range =>
case Index is
when 1 => return Enumeration_Type_Def_F_Elements;
when 2 => return Enumeration_Type_Def_F_Aspects;
when others => null;
end case;
when Rflx_Modular_Type_Def_Range =>
case Index is
when 1 => return Modular_Type_Def_F_Mod;
when others => null;
end case;
when Rflx_Range_Type_Def_Range =>
case Index is
when 1 => return Range_Type_Def_F_First;
when 2 => return Range_Type_Def_F_Last;
when 3 => return Range_Type_Def_F_Size;
when others => null;
end case;
when Rflx_Sequence_Type_Def_Range =>
case Index is
when 1 => return Sequence_Type_Def_F_Element_Type;
when others => null;
end case;
when Rflx_Type_Derivation_Def_Range =>
case Index is
when 1 => return Type_Derivation_Def_F_Base;
when others => null;
end case;
when others => null;
end case;

      pragma Warnings (Off, "value not in range of type");
      return (raise Bad_Type_Error with "Index is out of bounds");
      pragma Warnings (On, "value not in range of type");
   end Syntax_Field_Reference_From_Index;

   -------------------
   -- Syntax_Fields --
   -------------------

   function Syntax_Fields
     (Kind : R_F_L_X_Node_Kind_Type) return Syntax_Field_Reference_Array is
   begin
         return Syntax_Fields (Id_For_Kind (Kind), Concrete_Only => True);
   end Syntax_Fields;

   -------------------
   -- Syntax_Fields --
   -------------------

   function Syntax_Fields
     (Id            : Node_Type_Id;
      Concrete_Only : Boolean) return Syntax_Field_Reference_Array
   is
      Cursor : Any_Node_Type_Id := Id;

      Added_Fields : array (Syntax_Field_Reference) of Boolean :=
        (others => False);
      --  Set of field references that were added to Result

      Result : Syntax_Field_Reference_Array (1 .. Added_Fields'Length);
      --  Temporary to hold the result. We return Result (1 .. Last).

      Last : Natural := 0;
      --  Index of the last element in Result to return
   begin

         --  Go through the derivation chain for Id and collect fields. Do
         --  it in reverse order as we process base types last.
         while Cursor /= None loop
            declare
               Node_Desc : Node_Type_Descriptor renames
                  Node_Type_Descriptors (Cursor).all;
            begin
               for Field_Index in reverse Node_Desc.Fields'Range loop
                  declare
                     Field_Desc : Node_Field_Descriptor renames
                        Node_Desc.Fields (Field_Index).all;
                     Field      : Syntax_Field_Reference renames
                        Field_Desc.Field;
                  begin
                     --  Abstract fields share the same Syntax_Field_Reference
                     --  value with the corresponding concrete fields, so
                     --  collect fields only once. We process fields in reverse
                     --  order, so we know that concrete ones will be processed
                     --  before the abstract fields they override.
                     if not (Concrete_Only
                             and then Field_Desc.Is_Abstract_Or_Null)
                        and then not Added_Fields (Field)
                     then
                        Added_Fields (Field) := True;
                        Last := Last + 1;
                        Result (Last) := Field;
                     end if;
                  end;
               end loop;
               Cursor := Node_Desc.Base_Type;
            end;
         end loop;

         --  At this point, Result contains elements in the opposite order as
         --  expected, so reverse it.

         for I in 1 .. Last / 2 loop
            declare
               Other_I : constant Positive := Last - I + 1;
               Swap    : constant Syntax_Field_Reference := Result (I);
            begin
               Result (I) := Result (Other_I);
               Result (Other_I) := Swap;
            end;
         end loop;

         return Result (1 .. Last);

   end Syntax_Fields;

   -------------------
   -- Syntax_Fields --
   -------------------

   function Syntax_Fields
     (Id : Node_Type_Id) return Syntax_Field_Reference_Array is
   begin
      return Syntax_Fields (Id, Concrete_Only => False);
   end Syntax_Fields;


   -------------------
   -- Property_Name --
   -------------------

   function Property_Name (Property : Property_Reference) return Text_Type is
   begin
      return To_Text (Property_Descriptors (Property).Name);
   end Property_Name;

   --------------------------
   -- Property_Return_Type --
   --------------------------

   function Property_Return_Type
     (Property : Property_Reference) return Type_Constraint is
   begin
      return Property_Descriptors (Property).Return_Type;
   end Property_Return_Type;

   ---------------------------
   -- Check_Argument_Number --
   ---------------------------

   procedure Check_Argument_Number
     (Desc : Property_Descriptor; Argument_Number : Positive) is
   begin
      if Argument_Number not in Desc.Argument_Names'Range then
         raise Property_Error with "out-of-bounds argument number";
      end if;
   end Check_Argument_Number;

   -----------------------------
   -- Property_Argument_Types --
   -----------------------------

   function Property_Argument_Types
     (Property : Property_Reference) return Type_Constraint_Array is
   begin
      return Property_Descriptors (Property).Argument_Types;
   end Property_Argument_Types;

   ----------------------------
   -- Property_Argument_Name --
   ----------------------------

   function Property_Argument_Name
     (Property        : Property_Reference;
      Argument_Number : Positive) return Text_Type
   is
      Desc : Property_Descriptor renames Property_Descriptors (Property).all;
   begin
      Check_Argument_Number (Desc, Argument_Number);
      return To_Text
        (Property_Descriptors (Property).Argument_Names (Argument_Number).all);
   end Property_Argument_Name;

   -------------------------------------
   -- Property_Argument_Default_Value --
   -------------------------------------

   function Property_Argument_Default_Value
     (Property        : Property_Reference;
      Argument_Number : Positive) return Internal_Value
   is
      Desc : Property_Descriptor renames Property_Descriptors (Property).all;
   begin
      Check_Argument_Number (Desc, Argument_Number);
      return Desc.Argument_Default_Values (Argument_Number);
   end Property_Argument_Default_Value;

   ----------------
   -- Properties --
   ----------------

   function Properties (Kind : R_F_L_X_Node_Kind_Type) return Property_Reference_Array
   is
   begin
      return Properties (Id_For_Kind (Kind));
   end Properties;

   ----------------
   -- Properties --
   ----------------

   function Properties (Id : Node_Type_Id) return Property_Reference_Array is
      Cursor : Any_Node_Type_Id := Id;

      Result : Property_Reference_Array (1 .. Property_Descriptors'Length);
      --  Temporary to hold the result. We return Result (1 .. Last).

      Last : Natural := 0;
      --  Index of the last element in Result to return
   begin
      --  Go through the derivation chain for Id and collect properties. Do
      --  it in reverse order as we process base types last.

      while Cursor /= None loop
         declare
            Node_Desc : Node_Type_Descriptor renames
               Node_Type_Descriptors (Cursor).all;
         begin
            for Prop_Desc of reverse Node_Desc.Properties loop
               Last := Last + 1;
               Result (Last) := Prop_Desc;
            end loop;
            Cursor := Node_Desc.Base_Type;
         end;
      end loop;

      --  At this point, Result contains elements in the opposite order as
      --  expected, so reverse it.

      for I in 1 .. Last / 2 loop
         declare
            Other_I : constant Positive := Last - I + 1;
            Swap    : constant Property_Reference := Result (I);
         begin
            Result (I) := Result (Other_I);
            Result (Other_I) := Swap;
         end;
      end loop;

      return Result (1 .. Last);
   end Properties;


   ---------------------
   -- Token_Node_Kind --
   ---------------------

   function Token_Node_Kind (Kind : R_F_L_X_Node_Kind_Type) return Token_Kind is
      
   begin
         pragma Unreferenced (Kind);
         return (raise Program_Error);
   end Token_Node_Kind;

begin
   for D in Node_Type_Descriptors'Range loop
      DSL_Name_To_Node_Type.Insert (Node_Type_Descriptors (D).DSL_Name, D);
   end loop;
end Librflxlang.Introspection_Implementation;
