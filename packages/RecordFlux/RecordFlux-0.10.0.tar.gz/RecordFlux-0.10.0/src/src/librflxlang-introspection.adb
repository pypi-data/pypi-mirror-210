
with Librflxlang.Implementation;    use Librflxlang.Implementation;
with Librflxlang.Introspection_Implementation;
with Librflxlang.Public_Converters; use Librflxlang.Public_Converters;

package body Librflxlang.Introspection is

   package Impl renames Introspection_Implementation;

   --  TODO: move implementation of functions dealing with values (Satisfies,
   --  Eval_Property, ...) to Impl. This is not not done yet as substantial
   --  work is required in order to convert back and forth public values
   --  (structures, symbols) to their internal representations.

   function Allocate (Kind : Value_Kind) return Value_Type;
   --  Allocate a polymorphic value of the given kind

   pragma Warnings (Off, "is not referenced");
   function To_Internal_Value
     (Value : Any_Value_Type) return Impl.Internal_Value;
   function From_Internal_Value
     (Value : Impl.Internal_Value) return Any_Value_Type;
   pragma Warnings (On, "is not referenced");

   ------------
   -- Adjust --
   ------------

   overriding procedure Adjust (Self : in out Value_Access_Wrapper) is
   begin
      if Self.Value = null then
         return;
      end if;

      declare
         Rec : Value_Record renames Self.Value.all;
      begin
         Rec.Ref_Count := Rec.Ref_Count + 1;
      end;
   end Adjust;

   --------------
   -- Finalize --
   --------------

   overriding procedure Finalize (Self : in out Value_Access_Wrapper) is
   begin
      if Self.Value = null then
         return;
      end if;

      --  If Self is non-null, decrement the reference count of the referenced
      --  value.

      declare
         Rec : Value_Record renames Self.Value.all;
      begin
         Rec.Ref_Count := Rec.Ref_Count - 1;

         if Rec.Ref_Count = 0 then
            --  Reference count dropped to 0: time to free the value and what
            --  is inside.

            case Rec.Kind is
                     when R_F_L_X_Node_Array_Value =>
                        Free (Rec.R_F_L_X_Node_Array_Value);
               when others => null;
            end case;

            Free (Self.Value);
         end if;
      end;
   end Finalize;

   ----------
   -- Kind --
   ----------

   function Kind (Self : Value_Type) return Value_Kind is
   begin
      return Self.Value.Value.Kind;
   end Kind;

   --------------
   -- Allocate --
   --------------

   function Allocate (Kind : Value_Kind) return Value_Type is
      Result : Any_Value_Type;
   begin
      Result.Value.Value := new Value_Record (Kind);
      Result.Value.Value.Ref_Count := 1;
      return Result;
   end Allocate;

   -----------------------
   -- To_Internal_Value --
   -----------------------

   function To_Internal_Value
     (Value : Any_Value_Type) return Impl.Internal_Value is
   begin
      if Value = No_Value then
         return Impl.No_Internal_Value;
      end if;

      case Kind (Value) is
         when Boolean_Value =>
            return Impl.Create_Boolean (As_Boolean (Value));

         when Integer_Value =>
            return Impl.Create_Integer (As_Integer (Value));

         when Character_Value =>
            return Impl.Create_Character (As_Character (Value));

         when String_Value =>
            return Impl.Create_String (Create_String (As_String (Value)));

         when Node_Value =>
            return Impl.Create_Node (Unwrap_Entity (As_Node (Value)));

         when others =>
            --  For now we use this only to handle default values, so this
            --  should be unreachable.
            raise Program_Error;
      end case;
   end To_Internal_Value;

   -------------------------
   -- From_Internal_Value --
   -------------------------

   function From_Internal_Value
     (Value : Impl.Internal_Value) return Any_Value_Type is
   begin
      case Value.Kind is
         when None =>
            return No_Value;

         when Boolean_Value =>
            return Create_Boolean (Impl.As_Boolean (Value));

         when Integer_Value =>
            return Create_Integer (Impl.As_Integer (Value));

         when Character_Value =>
            return Create_Character (Impl.As_Character (Value));

         when String_Value =>
            return Create_String (Value.String_Value.Content);

            when Analysis_Unit_Kind_Value =>
               return Create_Analysis_Unit_Kind
                 (Impl.As_Analysis_Unit_Kind (Value));
            when Lookup_Kind_Value =>
               return Create_Lookup_Kind
                 (Impl.As_Lookup_Kind (Value));
            when Designated_Env_Kind_Value =>
               return Create_Designated_Env_Kind
                 (Impl.As_Designated_Env_Kind (Value));
            when Grammar_Rule_Value =>
               return Create_Grammar_Rule
                 (Impl.As_Grammar_Rule (Value));

         when Node_Value =>
            declare
               N : constant Internal_Entity := Impl.As_Node (Value);
            begin
               return Create_Node (Wrap_Node (N.Node, N.Info));
            end;
      end case;
   end From_Internal_Value;

   ----------------
   -- As_Boolean --
   ----------------

   function As_Boolean (Self : Value_Type) return Boolean is
   begin
      return Self.Value.Value.Boolean_Value;
   end As_Boolean;

   --------------------
   -- Create_Boolean --
   --------------------

   function Create_Boolean (Value : Boolean) return Value_Type is
   begin
      return Result : constant Value_Type := Allocate (Boolean_Value) do
         Result.Value.Value.Boolean_Value := Value;
      end return;
   end Create_Boolean;

   ----------------
   -- As_Integer --
   ----------------

   function As_Integer (Self : Value_Type) return Integer is
   begin
      return Self.Value.Value.Integer_Value;
   end As_Integer;

   --------------------
   -- Create_Integer --
   --------------------

   function Create_Integer (Value : Integer) return Value_Type is
   begin
      return Result : constant Value_Type := Allocate (Integer_Value) do
         Result.Value.Value.Integer_Value := Value;
      end return;
   end Create_Integer;

   --------------------
   -- As_Big_Integer --
   --------------------

   function As_Big_Integer (Self : Value_Type) return Big_Integer is
   begin
      return Result : Big_Integer do
         Result.Set (Self.Value.Value.Big_Integer_Value);
      end return;
   end As_Big_Integer;

   ------------------------
   -- Create_Big_Integer --
   ------------------------

   function Create_Big_Integer (Value : Big_Integer) return Value_Type is
   begin
      return Result : constant Value_Type := Allocate (Big_Integer_Value) do
         Result.Value.Value.Big_Integer_Value.Set (Value);
      end return;
   end Create_Big_Integer;

   ------------------
   -- As_Character --
   ------------------

   function As_Character (Self : Value_Type) return Character_Type is
   begin
      return Self.Value.Value.Character_Value;
   end As_Character;

   ----------------------
   -- Create_Character --
   ----------------------

   function Create_Character (Value : Character_Type) return Value_Type is
   begin
      return Result : constant Value_Type := Allocate (Character_Value) do
         Result.Value.Value.Character_Value := Value;
      end return;
   end Create_Character;

   ---------------
   -- As_String --
   ---------------

   function As_String (Self : Value_Type) return Text_Type is
   begin
      return To_Text (Self.Value.Value.String_Value);
   end As_String;

   -------------------
   -- Create_String --
   -------------------

   function Create_String (Value : Text_Type) return Value_Type is
   begin
      return Result : constant Value_Type := Allocate (String_Value) do
         Result.Value.Value.String_Value := To_Unbounded_Text (Value);
      end return;
   end Create_String;

   --------------
   -- As_Token --
   --------------

   function As_Token (Self : Value_Type) return Token_Reference is
   begin
      return Self.Value.Value.Token_Value;
   end As_Token;

   ------------------
   -- Create_Token --
   ------------------

   function Create_Token (Value : Token_Reference) return Value_Type is
   begin
      return Result : constant Value_Type := Allocate (Token_Value)
      do
         Result.Value.Value.Token_Value := Value;
      end return;
   end Create_Token;

   -----------------------
   -- As_Unbounded_Text --
   -----------------------

   function As_Unbounded_Text (Self : Value_Type) return Unbounded_Text_Type is
   begin
      return Self.Value.Value.Unbounded_Text_Value;
   end As_Unbounded_Text;

   ---------------------------
   -- Create_Unbounded_Text --
   ---------------------------

   function Create_Unbounded_Text
     (Value : Unbounded_Text_Type) return Value_Type is
   begin
      return Result : constant Value_Type := Allocate (Unbounded_Text_Value)
      do
         Result.Value.Value.Unbounded_Text_Value := Value;
      end return;
   end Create_Unbounded_Text;

   ----------------------
   -- As_Analysis_Unit --
   ----------------------

   function As_Analysis_Unit (Self : Value_Type) return Analysis_Unit is
   begin
      return Self.Value.Value.Analysis_Unit_Value;
   end As_Analysis_Unit;

   --------------------------
   -- Create_Analysis_Unit --
   --------------------------

   function Create_Analysis_Unit (Value : Analysis_Unit) return Value_Type is
   begin
      return Result : constant Value_Type := Allocate (Analysis_Unit_Value) do
         Result.Value.Value.Analysis_Unit_Value := Value;
      end return;
   end Create_Analysis_Unit;

   -------------
   -- As_Node --
   -------------

   function As_Node (Self : Value_Type) return R_F_L_X_Node is
   begin
      return Self.Value.Value.Node_Value;
   end As_Node;

   -----------------
   -- Create_Node --
   -----------------

   function Create_Node
     (Value : R_F_L_X_Node'Class) return Value_Type is
   begin
      return Result : constant Value_Type := Allocate (Node_Value) do
         Result.Value.Value.Node_Value := Value.As_R_F_L_X_Node;
      end return;
   end Create_Node;

      function As_Analysis_Unit_Kind
        (Self : Value_Type) return Analysis_Unit_Kind is
      begin
         return Self.Value.Value.Analysis_Unit_Kind_Value;
      end As_Analysis_Unit_Kind;

      function Create_Analysis_Unit_Kind
        (Value : Analysis_Unit_Kind) return Value_Type is
      begin
         return Result : constant Value_Type := Allocate
           (Analysis_Unit_Kind_Value)
         do
            Result.Value.Value.Analysis_Unit_Kind_Value := Value;
         end return;
      end Create_Analysis_Unit_Kind;
      function As_Lookup_Kind
        (Self : Value_Type) return Lookup_Kind is
      begin
         return Self.Value.Value.Lookup_Kind_Value;
      end As_Lookup_Kind;

      function Create_Lookup_Kind
        (Value : Lookup_Kind) return Value_Type is
      begin
         return Result : constant Value_Type := Allocate
           (Lookup_Kind_Value)
         do
            Result.Value.Value.Lookup_Kind_Value := Value;
         end return;
      end Create_Lookup_Kind;
      function As_Designated_Env_Kind
        (Self : Value_Type) return Designated_Env_Kind is
      begin
         return Self.Value.Value.Designated_Env_Kind_Value;
      end As_Designated_Env_Kind;

      function Create_Designated_Env_Kind
        (Value : Designated_Env_Kind) return Value_Type is
      begin
         return Result : constant Value_Type := Allocate
           (Designated_Env_Kind_Value)
         do
            Result.Value.Value.Designated_Env_Kind_Value := Value;
         end return;
      end Create_Designated_Env_Kind;
      function As_Grammar_Rule
        (Self : Value_Type) return Grammar_Rule is
      begin
         return Self.Value.Value.Grammar_Rule_Value;
      end As_Grammar_Rule;

      function Create_Grammar_Rule
        (Value : Grammar_Rule) return Value_Type is
      begin
         return Result : constant Value_Type := Allocate
           (Grammar_Rule_Value)
         do
            Result.Value.Value.Grammar_Rule_Value := Value;
         end return;
      end Create_Grammar_Rule;

         function As_R_F_L_X_Node_Array
           (Self : Value_Type) return R_F_L_X_Node_Array is
         begin
               return Result : R_F_L_X_Node_Array
                 (Self.Value.Value.R_F_L_X_Node_Array_Value'Range)
               do
                  for I in Result'Range loop
                        Result (I) :=
                           Self.Value.Value.R_F_L_X_Node_Array_Value.all (I);
                  end loop;
               end return;

         end As_R_F_L_X_Node_Array;

         function Create_R_F_L_X_Node_Array
           (Value : R_F_L_X_Node_Array) return Value_Type is
         begin
            return Result : constant Value_Type := Allocate
              (R_F_L_X_Node_Array_Value)
            do
                  Result.Value.Value.R_F_L_X_Node_Array_Value :=
                     new R_F_L_X_Node_Array (Value'Range);
                  for I in Value'Range loop
                        Result.Value.Value.R_F_L_X_Node_Array_Value.all (I) :=
                           Value (I);
                  end loop;

            end return;
         end Create_R_F_L_X_Node_Array;

   --------------
   -- DSL_Name --
   --------------

   function DSL_Name (Id : Node_Type_Id) return Text_Type is
   begin
      return Impl.DSL_Name (Id);
   end DSL_Name;

   ---------------------
   -- Lookup_DSL_Name --
   ---------------------

   function Lookup_DSL_Name (Name : Text_Type) return Any_Node_Type_Id is
   begin
      return Impl.Lookup_DSL_Name (Name);
   end Lookup_DSL_Name;

   -----------------
   -- Is_Abstract --
   -----------------

   function Is_Abstract (Id : Node_Type_Id) return Boolean is
   begin
      return Impl.Is_Abstract (Id);
   end Is_Abstract;

   --------------
   -- Kind_For --
   --------------

   function Kind_For (Id : Node_Type_Id) return R_F_L_X_Node_Kind_Type is
   begin
      return Impl.Kind_For (Id);
   end Kind_For;

   --------------------
   -- First_Kind_For --
   --------------------

   function First_Kind_For (Id : Node_Type_Id) return R_F_L_X_Node_Kind_Type is
   begin
      return Impl.First_Kind_For (Id);
   end First_Kind_For;

   -------------------
   -- Last_Kind_For --
   -------------------

   function Last_Kind_For (Id : Node_Type_Id) return R_F_L_X_Node_Kind_Type is
   begin
      return Impl.Last_Kind_For (Id);
   end Last_Kind_For;

   -----------------
   -- Id_For_Kind --
   -----------------

   function Id_For_Kind (Kind : R_F_L_X_Node_Kind_Type) return Node_Type_Id is
   begin
      return Impl.Id_For_Kind (Kind);
   end Id_For_Kind;

   ------------------
   -- Is_Root_Node --
   ------------------

   function Is_Root_Node (Id : Node_Type_Id) return Boolean is
   begin
      return Impl.Is_Root_Node (Id);
   end Is_Root_Node;

   ---------------
   -- Base_Type --
   ---------------

   function Base_Type (Id : Node_Type_Id) return Node_Type_Id is
   begin
      return Impl.Base_Type (Id);
   end Base_Type;

   -------------------
   -- Derived_Types --
   -------------------

   function Derived_Types (Id : Node_Type_Id) return Node_Type_Id_Array is
   begin
      return Impl.Derived_Types (Id);
   end Derived_Types;

   ---------------------
   -- Is_Derived_From --
   ---------------------

   function Is_Derived_From (Id, Parent : Node_Type_Id) return Boolean is
   begin
      return Impl.Is_Derived_From (Id, Parent);
   end Is_Derived_From;

   --------------
   -- DSL_Name --
   --------------

   function DSL_Name (Constraint : Type_Constraint) return Text_Type is
   begin
      
      case Constraint.Kind is
               when Boolean_Value =>
                  return "Bool";
               when Integer_Value =>
                  return "Int";
               when Big_Integer_Value =>
                  return "BigInt";
               when Character_Value =>
                  return "Character";
               when String_Value =>
                  return "String";
               when Token_Value =>
                  return "Token";
               when Unbounded_Text_Value =>
                  return "Symbol";
               when Analysis_Unit_Value =>
                  return "AnalysisUnit";
               when Analysis_Unit_Kind_Value =>
                  return "AnalysisUnitKind";
               when Lookup_Kind_Value =>
                  return "LookupKind";
               when Designated_Env_Kind_Value =>
                  return "DesignatedEnvKind";
               when Grammar_Rule_Value =>
                  return "GrammarRule";
               when R_F_L_X_Node_Array_Value =>
                  return "RFLXNode.entity.array";

         when Node_Value =>
            return DSL_Name (Constraint.Node_Type);
      end case;
   end DSL_Name;

   ---------------
   -- Satisfies --
   ---------------

   function Satisfies
     (Value : Value_Type; Constraint : Type_Constraint) return Boolean is
   begin
      if Value.Value.Value.Kind /= Constraint.Kind then
         return False;
      end if;

      case Constraint.Kind is
         when Node_Value =>
            return

              --  A null node always satisfies the type constraint
              Value.Value.Value.Node_Value.Is_Null

              --  Else, check that the type of the node is derived from the
              --  type of the constraint.
              or else Is_Derived_From
                (Id_For_Kind (Value.Value.Value.Node_Value.Kind),
                 Constraint.Node_Type);

         when others =>
            return True;
      end case;
   end Satisfies;

   

   ---------------------
   -- Enum_Last_Value --
   ---------------------

   function Enum_Last_Value (Kind : Enum_Value_Kind) return Enum_Value_Index is
   begin
      case Kind is
            when Analysis_Unit_Kind_Value =>
               return 2;
            when Lookup_Kind_Value =>
               return 3;
            when Designated_Env_Kind_Value =>
               return 4;
            when Grammar_Rule_Value =>
               return 89;
      end case;
   end Enum_Last_Value;

   ------------------------
   -- Enum_Default_Value --
   ------------------------

   function Enum_Default_Value
     (Kind : Enum_Value_Kind) return Any_Enum_Value_Index is
   begin
      case Kind is
            when Analysis_Unit_Kind_Value =>
                  return No_Enum_Value_Index;
            when Lookup_Kind_Value =>
                  return No_Enum_Value_Index;
            when Designated_Env_Kind_Value =>
                  return 1;
            when Grammar_Rule_Value =>
                  return No_Enum_Value_Index;
      end case;
   end Enum_Default_Value;

   ---------------------
   -- Enum_Value_Name --
   ---------------------

   function Enum_Value_Name
     (Kind : Enum_Value_Kind; Index : Enum_Value_Index) return Text_Type is
   begin
      case Kind is
            when Analysis_Unit_Kind_Value =>
               case Index is
                     when 1 =>
                        return "unit_specification";
                     when 2 =>
                        return "unit_body";

                  when others => null;
               end case;
            when Lookup_Kind_Value =>
               case Index is
                     when 1 =>
                        return "recursive";
                     when 2 =>
                        return "flat";
                     when 3 =>
                        return "minimal";

                  when others => null;
               end case;
            when Designated_Env_Kind_Value =>
               case Index is
                     when 1 =>
                        return "none";
                     when 2 =>
                        return "current_env";
                     when 3 =>
                        return "named_env";
                     when 4 =>
                        return "direct_env";

                  when others => null;
               end case;
            when Grammar_Rule_Value =>
               case Index is
                     when 1 =>
                        return "main_rule_rule";
                     when 2 =>
                        return "unqualified_identifier_rule";
                     when 3 =>
                        return "qualified_identifier_rule";
                     when 4 =>
                        return "numeric_literal_rule";
                     when 5 =>
                        return "variable_rule";
                     when 6 =>
                        return "sequence_aggregate_rule";
                     when 7 =>
                        return "string_literal_rule";
                     when 8 =>
                        return "concatenation_rule";
                     when 9 =>
                        return "primary_rule";
                     when 10 =>
                        return "paren_expression_rule";
                     when 11 =>
                        return "suffix_rule";
                     when 12 =>
                        return "factor_rule";
                     when 13 =>
                        return "term_rule";
                     when 14 =>
                        return "unop_term_rule";
                     when 15 =>
                        return "simple_expr_rule";
                     when 16 =>
                        return "relation_rule";
                     when 17 =>
                        return "expression_rule";
                     when 18 =>
                        return "quantified_expression_rule";
                     when 19 =>
                        return "comprehension_rule";
                     when 20 =>
                        return "call_rule";
                     when 21 =>
                        return "conversion_rule";
                     when 22 =>
                        return "null_message_aggregate_rule";
                     when 23 =>
                        return "message_aggregate_association_rule";
                     when 24 =>
                        return "message_aggregate_association_list_rule";
                     when 25 =>
                        return "message_aggregate_rule";
                     when 26 =>
                        return "extended_primary_rule";
                     when 27 =>
                        return "extended_paren_expression_rule";
                     when 28 =>
                        return "extended_choice_list_rule";
                     when 29 =>
                        return "extended_choices_rule";
                     when 30 =>
                        return "extended_case_expression_rule";
                     when 31 =>
                        return "extended_suffix_rule";
                     when 32 =>
                        return "extended_factor_rule";
                     when 33 =>
                        return "extended_term_rule";
                     when 34 =>
                        return "extended_unop_term_rule";
                     when 35 =>
                        return "extended_simple_expr_rule";
                     when 36 =>
                        return "extended_relation_rule";
                     when 37 =>
                        return "extended_expression_rule";
                     when 38 =>
                        return "aspect_rule";
                     when 39 =>
                        return "range_type_definition_rule";
                     when 40 =>
                        return "modular_type_definition_rule";
                     when 41 =>
                        return "integer_type_definition_rule";
                     when 42 =>
                        return "if_condition_rule";
                     when 43 =>
                        return "extended_if_condition_rule";
                     when 44 =>
                        return "then_rule";
                     when 45 =>
                        return "type_argument_rule";
                     when 46 =>
                        return "null_message_field_rule";
                     when 47 =>
                        return "message_field_rule";
                     when 48 =>
                        return "message_field_list_rule";
                     when 49 =>
                        return "value_range_rule";
                     when 50 =>
                        return "checksum_association_rule";
                     when 51 =>
                        return "checksum_aspect_rule";
                     when 52 =>
                        return "byte_order_aspect_rule";
                     when 53 =>
                        return "message_aspect_list_rule";
                     when 54 =>
                        return "message_type_definition_rule";
                     when 55 =>
                        return "positional_enumeration_rule";
                     when 56 =>
                        return "element_value_association_rule";
                     when 57 =>
                        return "named_enumeration_rule";
                     when 58 =>
                        return "enumeration_aspects_rule";
                     when 59 =>
                        return "enumeration_type_definition_rule";
                     when 60 =>
                        return "type_derivation_definition_rule";
                     when 61 =>
                        return "sequence_type_definition_rule";
                     when 62 =>
                        return "type_declaration_rule";
                     when 63 =>
                        return "type_refinement_rule";
                     when 64 =>
                        return "parameter_rule";
                     when 65 =>
                        return "parameter_list_rule";
                     when 66 =>
                        return "formal_function_declaration_rule";
                     when 67 =>
                        return "channel_declaration_rule";
                     when 68 =>
                        return "session_parameter_rule";
                     when 69 =>
                        return "renaming_declaration_rule";
                     when 70 =>
                        return "variable_declaration_rule";
                     when 71 =>
                        return "declaration_rule";
                     when 72 =>
                        return "description_aspect_rule";
                     when 73 =>
                        return "assignment_statement_rule";
                     when 74 =>
                        return "message_field_assignment_statement_rule";
                     when 75 =>
                        return "list_attribute_rule";
                     when 76 =>
                        return "reset_rule";
                     when 77 =>
                        return "attribute_statement_rule";
                     when 78 =>
                        return "action_rule";
                     when 79 =>
                        return "conditional_transition_rule";
                     when 80 =>
                        return "transition_rule";
                     when 81 =>
                        return "state_body_rule";
                     when 82 =>
                        return "state_rule";
                     when 83 =>
                        return "session_declaration_rule";
                     when 84 =>
                        return "basic_declaration_rule";
                     when 85 =>
                        return "basic_declarations_rule";
                     when 86 =>
                        return "package_declaration_rule";
                     when 87 =>
                        return "context_item_rule";
                     when 88 =>
                        return "context_clause_rule";
                     when 89 =>
                        return "specification_rule";

                  when others => null;
               end case;
      end case;

      return (raise Out_Of_Bounds_Error with "out of bounds enum value index");
   end Enum_Value_Name;

   -----------------------
   -- Lookup_Enum_Value --
   -----------------------

   function Lookup_Enum_Value
     (Kind : Enum_Value_Kind; Name : Text_Type) return Any_Enum_Value_Index is
   begin
      case Kind is
            when Analysis_Unit_Kind_Value =>
               if
                     Name = "unit_specification"
                  then
                     return 1;
                     elsif
                     Name = "unit_body"
                  then
                     return 2;
               end if;
            when Lookup_Kind_Value =>
               if
                     Name = "recursive"
                  then
                     return 1;
                     elsif
                     Name = "flat"
                  then
                     return 2;
                     elsif
                     Name = "minimal"
                  then
                     return 3;
               end if;
            when Designated_Env_Kind_Value =>
               if
                     Name = "none"
                  then
                     return 1;
                     elsif
                     Name = "current_env"
                  then
                     return 2;
                     elsif
                     Name = "named_env"
                  then
                     return 3;
                     elsif
                     Name = "direct_env"
                  then
                     return 4;
               end if;
            when Grammar_Rule_Value =>
               if
                     Name = "main_rule_rule"
                  then
                     return 1;
                     elsif
                     Name = "unqualified_identifier_rule"
                  then
                     return 2;
                     elsif
                     Name = "qualified_identifier_rule"
                  then
                     return 3;
                     elsif
                     Name = "numeric_literal_rule"
                  then
                     return 4;
                     elsif
                     Name = "variable_rule"
                  then
                     return 5;
                     elsif
                     Name = "sequence_aggregate_rule"
                  then
                     return 6;
                     elsif
                     Name = "string_literal_rule"
                  then
                     return 7;
                     elsif
                     Name = "concatenation_rule"
                  then
                     return 8;
                     elsif
                     Name = "primary_rule"
                  then
                     return 9;
                     elsif
                     Name = "paren_expression_rule"
                  then
                     return 10;
                     elsif
                     Name = "suffix_rule"
                  then
                     return 11;
                     elsif
                     Name = "factor_rule"
                  then
                     return 12;
                     elsif
                     Name = "term_rule"
                  then
                     return 13;
                     elsif
                     Name = "unop_term_rule"
                  then
                     return 14;
                     elsif
                     Name = "simple_expr_rule"
                  then
                     return 15;
                     elsif
                     Name = "relation_rule"
                  then
                     return 16;
                     elsif
                     Name = "expression_rule"
                  then
                     return 17;
                     elsif
                     Name = "quantified_expression_rule"
                  then
                     return 18;
                     elsif
                     Name = "comprehension_rule"
                  then
                     return 19;
                     elsif
                     Name = "call_rule"
                  then
                     return 20;
                     elsif
                     Name = "conversion_rule"
                  then
                     return 21;
                     elsif
                     Name = "null_message_aggregate_rule"
                  then
                     return 22;
                     elsif
                     Name = "message_aggregate_association_rule"
                  then
                     return 23;
                     elsif
                     Name = "message_aggregate_association_list_rule"
                  then
                     return 24;
                     elsif
                     Name = "message_aggregate_rule"
                  then
                     return 25;
                     elsif
                     Name = "extended_primary_rule"
                  then
                     return 26;
                     elsif
                     Name = "extended_paren_expression_rule"
                  then
                     return 27;
                     elsif
                     Name = "extended_choice_list_rule"
                  then
                     return 28;
                     elsif
                     Name = "extended_choices_rule"
                  then
                     return 29;
                     elsif
                     Name = "extended_case_expression_rule"
                  then
                     return 30;
                     elsif
                     Name = "extended_suffix_rule"
                  then
                     return 31;
                     elsif
                     Name = "extended_factor_rule"
                  then
                     return 32;
                     elsif
                     Name = "extended_term_rule"
                  then
                     return 33;
                     elsif
                     Name = "extended_unop_term_rule"
                  then
                     return 34;
                     elsif
                     Name = "extended_simple_expr_rule"
                  then
                     return 35;
                     elsif
                     Name = "extended_relation_rule"
                  then
                     return 36;
                     elsif
                     Name = "extended_expression_rule"
                  then
                     return 37;
                     elsif
                     Name = "aspect_rule"
                  then
                     return 38;
                     elsif
                     Name = "range_type_definition_rule"
                  then
                     return 39;
                     elsif
                     Name = "modular_type_definition_rule"
                  then
                     return 40;
                     elsif
                     Name = "integer_type_definition_rule"
                  then
                     return 41;
                     elsif
                     Name = "if_condition_rule"
                  then
                     return 42;
                     elsif
                     Name = "extended_if_condition_rule"
                  then
                     return 43;
                     elsif
                     Name = "then_rule"
                  then
                     return 44;
                     elsif
                     Name = "type_argument_rule"
                  then
                     return 45;
                     elsif
                     Name = "null_message_field_rule"
                  then
                     return 46;
                     elsif
                     Name = "message_field_rule"
                  then
                     return 47;
                     elsif
                     Name = "message_field_list_rule"
                  then
                     return 48;
                     elsif
                     Name = "value_range_rule"
                  then
                     return 49;
                     elsif
                     Name = "checksum_association_rule"
                  then
                     return 50;
                     elsif
                     Name = "checksum_aspect_rule"
                  then
                     return 51;
                     elsif
                     Name = "byte_order_aspect_rule"
                  then
                     return 52;
                     elsif
                     Name = "message_aspect_list_rule"
                  then
                     return 53;
                     elsif
                     Name = "message_type_definition_rule"
                  then
                     return 54;
                     elsif
                     Name = "positional_enumeration_rule"
                  then
                     return 55;
                     elsif
                     Name = "element_value_association_rule"
                  then
                     return 56;
                     elsif
                     Name = "named_enumeration_rule"
                  then
                     return 57;
                     elsif
                     Name = "enumeration_aspects_rule"
                  then
                     return 58;
                     elsif
                     Name = "enumeration_type_definition_rule"
                  then
                     return 59;
                     elsif
                     Name = "type_derivation_definition_rule"
                  then
                     return 60;
                     elsif
                     Name = "sequence_type_definition_rule"
                  then
                     return 61;
                     elsif
                     Name = "type_declaration_rule"
                  then
                     return 62;
                     elsif
                     Name = "type_refinement_rule"
                  then
                     return 63;
                     elsif
                     Name = "parameter_rule"
                  then
                     return 64;
                     elsif
                     Name = "parameter_list_rule"
                  then
                     return 65;
                     elsif
                     Name = "formal_function_declaration_rule"
                  then
                     return 66;
                     elsif
                     Name = "channel_declaration_rule"
                  then
                     return 67;
                     elsif
                     Name = "session_parameter_rule"
                  then
                     return 68;
                     elsif
                     Name = "renaming_declaration_rule"
                  then
                     return 69;
                     elsif
                     Name = "variable_declaration_rule"
                  then
                     return 70;
                     elsif
                     Name = "declaration_rule"
                  then
                     return 71;
                     elsif
                     Name = "description_aspect_rule"
                  then
                     return 72;
                     elsif
                     Name = "assignment_statement_rule"
                  then
                     return 73;
                     elsif
                     Name = "message_field_assignment_statement_rule"
                  then
                     return 74;
                     elsif
                     Name = "list_attribute_rule"
                  then
                     return 75;
                     elsif
                     Name = "reset_rule"
                  then
                     return 76;
                     elsif
                     Name = "attribute_statement_rule"
                  then
                     return 77;
                     elsif
                     Name = "action_rule"
                  then
                     return 78;
                     elsif
                     Name = "conditional_transition_rule"
                  then
                     return 79;
                     elsif
                     Name = "transition_rule"
                  then
                     return 80;
                     elsif
                     Name = "state_body_rule"
                  then
                     return 81;
                     elsif
                     Name = "state_rule"
                  then
                     return 82;
                     elsif
                     Name = "session_declaration_rule"
                  then
                     return 83;
                     elsif
                     Name = "basic_declaration_rule"
                  then
                     return 84;
                     elsif
                     Name = "basic_declarations_rule"
                  then
                     return 85;
                     elsif
                     Name = "package_declaration_rule"
                  then
                     return 86;
                     elsif
                     Name = "context_item_rule"
                  then
                     return 87;
                     elsif
                     Name = "context_clause_rule"
                  then
                     return 88;
                     elsif
                     Name = "specification_rule"
                  then
                     return 89;
               end if;
      end case;

      return No_Enum_Value_Index;
   end Lookup_Enum_Value;

   -----------------
   -- Create_Enum --
   -----------------

   function Create_Enum
     (Kind : Enum_Value_Kind; Index : Enum_Value_Index) return Value_Type is
   begin
      case Kind is
            when Analysis_Unit_Kind_Value =>
               case Index is
                     when 1 =>
                        return Create_Analysis_Unit_Kind (Unit_Specification);
                     when 2 =>
                        return Create_Analysis_Unit_Kind (Unit_Body);

                  when others => null;
               end case;
            when Lookup_Kind_Value =>
               case Index is
                     when 1 =>
                        return Create_Lookup_Kind (Recursive);
                     when 2 =>
                        return Create_Lookup_Kind (Flat);
                     when 3 =>
                        return Create_Lookup_Kind (Minimal);

                  when others => null;
               end case;
            when Designated_Env_Kind_Value =>
               case Index is
                     when 1 =>
                        return Create_Designated_Env_Kind (None);
                     when 2 =>
                        return Create_Designated_Env_Kind (Current_Env);
                     when 3 =>
                        return Create_Designated_Env_Kind (Named_Env);
                     when 4 =>
                        return Create_Designated_Env_Kind (Direct_Env);

                  when others => null;
               end case;
            when Grammar_Rule_Value =>
               case Index is
                     when 1 =>
                        return Create_Grammar_Rule (Main_Rule_Rule);
                     when 2 =>
                        return Create_Grammar_Rule (Unqualified_Identifier_Rule);
                     when 3 =>
                        return Create_Grammar_Rule (Qualified_Identifier_Rule);
                     when 4 =>
                        return Create_Grammar_Rule (Numeric_Literal_Rule);
                     when 5 =>
                        return Create_Grammar_Rule (Variable_Rule);
                     when 6 =>
                        return Create_Grammar_Rule (Sequence_Aggregate_Rule);
                     when 7 =>
                        return Create_Grammar_Rule (String_Literal_Rule);
                     when 8 =>
                        return Create_Grammar_Rule (Concatenation_Rule);
                     when 9 =>
                        return Create_Grammar_Rule (Primary_Rule);
                     when 10 =>
                        return Create_Grammar_Rule (Paren_Expression_Rule);
                     when 11 =>
                        return Create_Grammar_Rule (Suffix_Rule);
                     when 12 =>
                        return Create_Grammar_Rule (Factor_Rule);
                     when 13 =>
                        return Create_Grammar_Rule (Term_Rule);
                     when 14 =>
                        return Create_Grammar_Rule (Unop_Term_Rule);
                     when 15 =>
                        return Create_Grammar_Rule (Simple_Expr_Rule);
                     when 16 =>
                        return Create_Grammar_Rule (Relation_Rule);
                     when 17 =>
                        return Create_Grammar_Rule (Expression_Rule);
                     when 18 =>
                        return Create_Grammar_Rule (Quantified_Expression_Rule);
                     when 19 =>
                        return Create_Grammar_Rule (Comprehension_Rule);
                     when 20 =>
                        return Create_Grammar_Rule (Call_Rule);
                     when 21 =>
                        return Create_Grammar_Rule (Conversion_Rule);
                     when 22 =>
                        return Create_Grammar_Rule (Null_Message_Aggregate_Rule);
                     when 23 =>
                        return Create_Grammar_Rule (Message_Aggregate_Association_Rule);
                     when 24 =>
                        return Create_Grammar_Rule (Message_Aggregate_Association_List_Rule);
                     when 25 =>
                        return Create_Grammar_Rule (Message_Aggregate_Rule);
                     when 26 =>
                        return Create_Grammar_Rule (Extended_Primary_Rule);
                     when 27 =>
                        return Create_Grammar_Rule (Extended_Paren_Expression_Rule);
                     when 28 =>
                        return Create_Grammar_Rule (Extended_Choice_List_Rule);
                     when 29 =>
                        return Create_Grammar_Rule (Extended_Choices_Rule);
                     when 30 =>
                        return Create_Grammar_Rule (Extended_Case_Expression_Rule);
                     when 31 =>
                        return Create_Grammar_Rule (Extended_Suffix_Rule);
                     when 32 =>
                        return Create_Grammar_Rule (Extended_Factor_Rule);
                     when 33 =>
                        return Create_Grammar_Rule (Extended_Term_Rule);
                     when 34 =>
                        return Create_Grammar_Rule (Extended_Unop_Term_Rule);
                     when 35 =>
                        return Create_Grammar_Rule (Extended_Simple_Expr_Rule);
                     when 36 =>
                        return Create_Grammar_Rule (Extended_Relation_Rule);
                     when 37 =>
                        return Create_Grammar_Rule (Extended_Expression_Rule);
                     when 38 =>
                        return Create_Grammar_Rule (Aspect_Rule);
                     when 39 =>
                        return Create_Grammar_Rule (Range_Type_Definition_Rule);
                     when 40 =>
                        return Create_Grammar_Rule (Modular_Type_Definition_Rule);
                     when 41 =>
                        return Create_Grammar_Rule (Integer_Type_Definition_Rule);
                     when 42 =>
                        return Create_Grammar_Rule (If_Condition_Rule);
                     when 43 =>
                        return Create_Grammar_Rule (Extended_If_Condition_Rule);
                     when 44 =>
                        return Create_Grammar_Rule (Then_Rule);
                     when 45 =>
                        return Create_Grammar_Rule (Type_Argument_Rule);
                     when 46 =>
                        return Create_Grammar_Rule (Null_Message_Field_Rule);
                     when 47 =>
                        return Create_Grammar_Rule (Message_Field_Rule);
                     when 48 =>
                        return Create_Grammar_Rule (Message_Field_List_Rule);
                     when 49 =>
                        return Create_Grammar_Rule (Value_Range_Rule);
                     when 50 =>
                        return Create_Grammar_Rule (Checksum_Association_Rule);
                     when 51 =>
                        return Create_Grammar_Rule (Checksum_Aspect_Rule);
                     when 52 =>
                        return Create_Grammar_Rule (Byte_Order_Aspect_Rule);
                     when 53 =>
                        return Create_Grammar_Rule (Message_Aspect_List_Rule);
                     when 54 =>
                        return Create_Grammar_Rule (Message_Type_Definition_Rule);
                     when 55 =>
                        return Create_Grammar_Rule (Positional_Enumeration_Rule);
                     when 56 =>
                        return Create_Grammar_Rule (Element_Value_Association_Rule);
                     when 57 =>
                        return Create_Grammar_Rule (Named_Enumeration_Rule);
                     when 58 =>
                        return Create_Grammar_Rule (Enumeration_Aspects_Rule);
                     when 59 =>
                        return Create_Grammar_Rule (Enumeration_Type_Definition_Rule);
                     when 60 =>
                        return Create_Grammar_Rule (Type_Derivation_Definition_Rule);
                     when 61 =>
                        return Create_Grammar_Rule (Sequence_Type_Definition_Rule);
                     when 62 =>
                        return Create_Grammar_Rule (Type_Declaration_Rule);
                     when 63 =>
                        return Create_Grammar_Rule (Type_Refinement_Rule);
                     when 64 =>
                        return Create_Grammar_Rule (Parameter_Rule);
                     when 65 =>
                        return Create_Grammar_Rule (Parameter_List_Rule);
                     when 66 =>
                        return Create_Grammar_Rule (Formal_Function_Declaration_Rule);
                     when 67 =>
                        return Create_Grammar_Rule (Channel_Declaration_Rule);
                     when 68 =>
                        return Create_Grammar_Rule (Session_Parameter_Rule);
                     when 69 =>
                        return Create_Grammar_Rule (Renaming_Declaration_Rule);
                     when 70 =>
                        return Create_Grammar_Rule (Variable_Declaration_Rule);
                     when 71 =>
                        return Create_Grammar_Rule (Declaration_Rule);
                     when 72 =>
                        return Create_Grammar_Rule (Description_Aspect_Rule);
                     when 73 =>
                        return Create_Grammar_Rule (Assignment_Statement_Rule);
                     when 74 =>
                        return Create_Grammar_Rule (Message_Field_Assignment_Statement_Rule);
                     when 75 =>
                        return Create_Grammar_Rule (List_Attribute_Rule);
                     when 76 =>
                        return Create_Grammar_Rule (Reset_Rule);
                     when 77 =>
                        return Create_Grammar_Rule (Attribute_Statement_Rule);
                     when 78 =>
                        return Create_Grammar_Rule (Action_Rule);
                     when 79 =>
                        return Create_Grammar_Rule (Conditional_Transition_Rule);
                     when 80 =>
                        return Create_Grammar_Rule (Transition_Rule);
                     when 81 =>
                        return Create_Grammar_Rule (State_Body_Rule);
                     when 82 =>
                        return Create_Grammar_Rule (State_Rule);
                     when 83 =>
                        return Create_Grammar_Rule (Session_Declaration_Rule);
                     when 84 =>
                        return Create_Grammar_Rule (Basic_Declaration_Rule);
                     when 85 =>
                        return Create_Grammar_Rule (Basic_Declarations_Rule);
                     when 86 =>
                        return Create_Grammar_Rule (Package_Declaration_Rule);
                     when 87 =>
                        return Create_Grammar_Rule (Context_Item_Rule);
                     when 88 =>
                        return Create_Grammar_Rule (Context_Clause_Rule);
                     when 89 =>
                        return Create_Grammar_Rule (Specification_Rule);

                  when others => null;
               end case;
      end case;

      return (raise Out_Of_Bounds_Error with "out of bounds enum value index");
   end Create_Enum;

   ----------------
   -- Enum_Index --
   ----------------

   function Enum_Index (Value : Value_Type) return Enum_Value_Index is
   begin
      case Kind (Value) is
            when Analysis_Unit_Kind_Value =>
               return Analysis_Unit_Kind'Pos (As_Analysis_Unit_Kind (Value)) + 1;
            when Lookup_Kind_Value =>
               return Lookup_Kind'Pos (As_Lookup_Kind (Value)) + 1;
            when Designated_Env_Kind_Value =>
               return Designated_Env_Kind'Pos (As_Designated_Env_Kind (Value)) + 1;
            when Grammar_Rule_Value =>
               return Grammar_Rule'Pos (As_Grammar_Rule (Value)) + 1;

         when others =>
            return (raise Bad_Type_Error with "not an enum value");
      end case;
   end Enum_Index;

   

   ------------------------------
   -- Array_Element_Constraint --
   ------------------------------

   function Array_Element_Constraint
     (Kind : Array_Value_Kind) return Type_Constraint is
   begin
      case Kind is
            
            when R_F_L_X_Node_Array_Value =>
                  
                  return (Kind      => Node_Value,
                          Node_Type => Common.R_F_L_X_Node_Type_Id);
      end case;
   end Array_Element_Constraint;

   ------------------
   -- Array_Length --
   ------------------

   function Array_Length (Self : Value_Type) return Natural is
   begin
      case Kind (Self) is
            when R_F_L_X_Node_Array_Value =>
               return Self.Value.Value.R_F_L_X_Node_Array_Value.all'Length;

         when others =>
            return (raise Bad_Type_Error with "input value is not an array");
      end case;
   end Array_Length;

   -------------------
   -- Array_Element --
   -------------------

   function Array_Element
     (Self : Value_Type; Index : Positive) return Value_Type is
   begin
      case Kind (Self) is
            when R_F_L_X_Node_Array_Value =>
               declare
                  A : R_F_L_X_Node_Array renames
                     Self.Value.Value.R_F_L_X_Node_Array_Value.all;
               begin
                  if Index not in A'Range then
                     raise Out_Of_Bounds_Error with "index of array bounds";
                  end if;
                  return Create_Node
                    (A (Index));
               end;

         when others =>
            return (raise Bad_Type_Error with "input value is not an array");
      end case;
   end Array_Element;

   ------------------
   -- Create_Array --
   ------------------

   function Create_Array
     (Kind : Array_Value_Kind; Values : Value_Array) return Value_Type
   is
      Elt_Cons : constant Type_Constraint := Array_Element_Constraint (Kind);
   begin
      --  First check that all input values have the expected type

      for I in Values'Range loop
         if not Satisfies (Values (I), Elt_Cons) then
            raise Bad_Type_Error with "invalid value at index " & I'Image;
         end if;
      end loop;

      --  Then create the array to return

      case Kind is
            
            when R_F_L_X_Node_Array_Value =>
               declare
                  A : R_F_L_X_Node_Array (1 .. Values'Length);
               begin
                  for I in Values'Range loop
                        
                        A (I) :=
                           As_Node (Values (I))
                        ;

                  end loop;
                  return Create_R_F_L_X_Node_Array (A);
               end;
      end case;
   end Create_Array;

   -------------------
   -- Struct_Fields --
   -------------------

   function Struct_Fields
     (Kind : Struct_Value_Kind) return Struct_Field_Reference_Array is
   begin
      pragma Warnings (Off, "value not in range of type");
      return Impl.Struct_Fields (Kind);
      pragma Warnings (On, "value not in range of type");
   end Struct_Fields;

   -------------------
   -- Create_Struct --
   -------------------

   pragma Warnings (Off, "referenced");
   function Create_Struct
     (Kind : Struct_Value_Kind; Values : Value_Array) return Value_Type
   is
      pragma Warnings (On, "referenced");
   begin
         return (raise Program_Error);
   end Create_Struct;

   -----------------
   -- Member_Name --
   -----------------

   function Member_Name (Member : Member_Reference) return Text_Type is
   begin
      return Impl.Member_Name (Member);
   end Member_Name;

   -----------------
   -- Member_Type --
   -----------------

   function Member_Type (Member : Member_Reference) return Type_Constraint is
   begin
      return Impl.Member_Type (Member);
   end Member_Type;

   function Eval_Member
     (Prefix    : Value_Type;
      Member    : Member_Reference;
      Arguments : Value_Array) return Value_Type
   is
      Prefix_Val : Value_Record renames Prefix.Value.Value.all;
   begin
      case Prefix_Val.Kind is
      when Struct_Value_Kind =>
         if Member not in Struct_Field_Reference then
            return (raise Bad_Type_Error with "no such member");
         elsif Arguments'Length /= 0 then
            return (raise Bad_Type_Error
                    with "struct fields take no argument");
         else
            pragma Warnings (Off, "value not in range of type");
            return Eval_Member (Prefix, Member);
            pragma Warnings (On, "value not in range of type");
         end if;

      when Node_Value =>
         return Eval_Member (Prefix_Val.Node_Value, Member, Arguments);

      when others =>
         return (raise Bad_Type_Error with "invalid prefix type");
      end case;
   end Eval_Member;

   -----------------
   -- Eval_Member --
   -----------------

   pragma Warnings (Off, "referenced");
   function Eval_Member
     (Prefix : Value_Type; Field : Struct_Field_Reference) return Value_Type
   is
      pragma Warnings (On, "referenced");
      Prefix_Val : Value_Record renames Prefix.Value.Value.all;
   begin
      case Prefix_Val.Kind is


      when others =>
         return (raise Program_Error);
      end case;

   end Eval_Member;

   -----------------
   -- Eval_Member --
   -----------------

   function Eval_Member
     (Node      : R_F_L_X_Node'Class;
      Member    : Node_Member_Reference;
      Arguments : Value_Array) return Value_Type is
   begin
      case Member is
         when Syntax_Field_Reference =>
            if Arguments'Length > 0 then
               raise Bad_Type_Error with "fields take no argument";
            end if;
            pragma Warnings (Off, "value not in range of type");
            return Create_Node (Eval_Syntax_Field (Node, Member));
            pragma Warnings (On, "value not in range of type");

         when Property_Reference =>
            return Eval_Property (Node, Member, Arguments);
      end case;
   end Eval_Member;

   -------------------
   -- Lookup_Member --
   -------------------

   function Lookup_Member
     (Prefix : Value_Type;
      Name   : Text_Type) return Any_Member_Reference
   is
      Prefix_Val : Value_Record renames Prefix.Value.Value.all;
   begin
      case Prefix_Val.Kind is
      when Struct_Value_Kind =>
         pragma Warnings (Off, "value not in range of type");
         return Impl.Lookup_Member_Struct (Prefix_Val.Kind, Name);
         pragma Warnings (On, "value not in range of type");

      when Node_Value =>
         declare
            Node : constant R_F_L_X_Node := Prefix_Val.Node_Value;
         begin
            if Node.Is_Null then
               raise Bad_Type_Error with "invalid null prefix node";
            end if;
            return Impl.Lookup_Member_Node (Impl.Id_For_Kind (Node.Kind), Name);
         end;

      when others =>
         return (raise Bad_Type_Error with "invalid prefix type");
      end case;
   end Lookup_Member;

   function Lookup_Member
     (Id   : Node_Type_Id;
      Name : Text_Type) return Any_Member_Reference is
   begin
      return Impl.Lookup_Member_Node (Id, Name);
   end Lookup_Member;

   -----------------------
   -- Eval_Syntax_Field --
   -----------------------

   function Eval_Syntax_Field
     (Node  : R_F_L_X_Node'Class;
      Field : Syntax_Field_Reference) return R_F_L_X_Node
   is
      Ent : constant Internal_Entity := Unwrap_Entity (Node);

      pragma Warnings (Off, "value not in range of type");
      Result : constant Bare_R_F_L_X_Node :=
         Impl.Eval_Syntax_Field (Ent.Node, Field);
      pragma Warnings (On, "value not in range of type");
   begin
      return Wrap_Node (Result, Ent.Info);
   end Eval_Syntax_Field;

   -----------
   -- Index --
   -----------

   function Index
     (Kind : R_F_L_X_Node_Kind_Type; Field : Syntax_Field_Reference) return Positive is
   begin
      pragma Warnings (Off, "value not in range of type");
      return Impl.Index (Kind, Field);
      pragma Warnings (On, "value not in range of type");
   end Index;

   ---------------------------------------
   -- Syntax_Field_Reference_From_Index --
   ---------------------------------------

   function Syntax_Field_Reference_From_Index
     (Kind : R_F_L_X_Node_Kind_Type; Index : Positive) return Syntax_Field_Reference is
   begin
      pragma Warnings (Off, "value not in range of type");
      return Impl.Syntax_Field_Reference_From_Index (Kind, Index);
      pragma Warnings (On, "value not in range of type");
   end Syntax_Field_Reference_From_Index;

   -------------------
   -- Syntax_Fields --
   -------------------

   function Syntax_Fields
     (Kind : R_F_L_X_Node_Kind_Type) return Syntax_Field_Reference_Array is
   begin
      return Impl.Syntax_Fields (Kind);
   end Syntax_Fields;

   -------------------
   -- Syntax_Fields --
   -------------------

   function Syntax_Fields
     (Id : Node_Type_Id) return Syntax_Field_Reference_Array is
   begin
      return Impl.Syntax_Fields (Id);
   end Syntax_Fields;

   -----------------------------
   -- Property_Argument_Types --
   -----------------------------

   function Property_Argument_Types
     (Property : Property_Reference) return Type_Constraint_Array is
   begin
      return Impl.Property_Argument_Types (Property);
   end Property_Argument_Types;

   ----------------------------
   -- Property_Argument_Name --
   ----------------------------

   function Property_Argument_Name
     (Property        : Property_Reference;
      Argument_Number : Positive) return Text_Type is
   begin
      return Impl.Property_Argument_Name (Property, Argument_Number);
   end Property_Argument_Name;

   -------------------------------------
   -- Property_Argument_Default_Value --
   -------------------------------------

   function Property_Argument_Default_Value
     (Property        : Property_Reference;
      Argument_Number : Positive) return Any_Value_Type
   is
      Desc : Impl.Property_Descriptor renames
         Impl.Property_Descriptors (Property).all;
   begin
      Impl.Check_Argument_Number (Desc, Argument_Number);
      return From_Internal_Value
        (Desc.Argument_Default_Values (Argument_Number));
   end Property_Argument_Default_Value;

   -------------------
   -- Eval_Property --
   -------------------

   function Eval_Property
     (Node      : R_F_L_X_Node'Class;
      Property  : Property_Reference;
      Arguments : Value_Array) return Value_Type
   is
      Kind   : constant R_F_L_X_Node_Kind_Type := Node.Kind;
      Desc   : Impl.Property_Descriptor renames
         Impl.Property_Descriptors (Property).all;
      Result : Any_Value_Type := No_Value;
   begin
      --  First, check that arguments match the property signature

      if Arguments'Length /= Desc.Arity then
         raise Bad_Type_Error with "invalid number of arguments";
      end if;

      for I in Desc.Argument_Types'Range loop
         declare
            Arg : Value_Type renames Arguments (I - 1 + Arguments'First);
         begin
            if not Satisfies (Arg, Desc.Argument_Types (I)) then
               raise Bad_Type_Error with
                  "invalid type for argument " & Desc.Argument_Names (I).all;
            end if;
         end;
      end loop;

      --  Now, we can proceed with the property evaluation

      
      case Property is
when R_F_L_X_Node_Parent =>
Result := Create_Node (Node.Parent);
when R_F_L_X_Node_Parents =>
declare
With_Self : constant Boolean :=
As_Boolean (Arguments (Arguments'First + 0));
begin
Result := Create_R_F_L_X_Node_Array (Node.Parents (With_Self));
end;
when R_F_L_X_Node_Children =>
Result := Create_R_F_L_X_Node_Array (Node.Children);
when R_F_L_X_Node_Token_Start =>
Result := Create_Token (Node.Token_Start);
when R_F_L_X_Node_Token_End =>
Result := Create_Token (Node.Token_End);
when R_F_L_X_Node_Child_Index =>
Result := Create_Integer (Node.Child_Index);
when R_F_L_X_Node_Previous_Sibling =>
Result := Create_Node (Node.Previous_Sibling);
when R_F_L_X_Node_Next_Sibling =>
Result := Create_Node (Node.Next_Sibling);
when R_F_L_X_Node_Unit =>
Result := Create_Analysis_Unit (Node.Unit);
when R_F_L_X_Node_Is_Ghost =>
Result := Create_Boolean (Node.Is_Ghost);
when R_F_L_X_Node_Full_Sloc_Image =>
Result := Create_String (Node.Full_Sloc_Image);
when others => null;
end case;
pragma Unreferenced (Kind);

      if Result = No_Value then
         raise Bad_Type_Error with "no such field on this node";
      end if;
      return Result;
   end Eval_Property;

   ----------------
   -- Properties --
   ----------------

   function Properties (Kind : R_F_L_X_Node_Kind_Type) return Property_Reference_Array
   is
   begin
      return Impl.Properties (Kind);
   end Properties;

   ----------------
   -- Properties --
   ----------------

   function Properties (Id : Node_Type_Id) return Property_Reference_Array is
   begin
      return Impl.Properties (Id);
   end Properties;

   ---------------------
   -- Token_Node_Kind --
   ---------------------

   function Token_Node_Kind (Kind : R_F_L_X_Node_Kind_Type) return Token_Kind is
   begin
      return Impl.Token_Node_Kind (Kind);
   end Token_Node_Kind;

end Librflxlang.Introspection;
