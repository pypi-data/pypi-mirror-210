
with Ada.Containers.Hashed_Maps;
with Ada.Strings.Unbounded; use Ada.Strings.Unbounded;
with Ada.Strings.Unbounded.Hash;

with Librflxlang.Implementation; use Librflxlang.Implementation;
with Librflxlang.Common;         use Librflxlang.Common;

private package Librflxlang.Introspection_Implementation is

   use Support.Text;

   ------------------------
   -- Polymorphic values --
   ------------------------

   --  TODO: for now, support only value types that are required to represent
   --  default values for property arguments.

   subtype Internal_Value_Kind is Any_Value_Kind
      with Static_Predicate => Internal_Value_Kind in
         None | Boolean_Value | Integer_Value | Character_Value | String_Value
       | Analysis_Unit_Kind_Value
       | Lookup_Kind_Value
       | Designated_Env_Kind_Value
       | Grammar_Rule_Value
       | Node_Value;

   type Internal_Value (Kind : Internal_Value_Kind := None) is record
      case Kind is
         when None =>
            null;

         when Boolean_Value =>
            Boolean_Value : Boolean;

         when Integer_Value =>
            Integer_Value : Integer;

         when Character_Value =>
            Character_Value : Character_Type;

         when String_Value =>
            String_Value : String_Type;

         when Analysis_Unit_Kind_Value =>
            Analysis_Unit_Kind_Value : Analysis_Unit_Kind;
         when Lookup_Kind_Value =>
            Lookup_Kind_Value : Lookup_Kind;
         when Designated_Env_Kind_Value =>
            Designated_Env_Kind_Value : Designated_Env_Kind;
         when Grammar_Rule_Value =>
            Grammar_Rule_Value : Grammar_Rule;

         when Node_Value =>
            Node_Value : Internal_Entity;
      end case;
   end record;

   No_Internal_Value : constant Internal_Value := (Kind => None);

   type Internal_Value_Array is array (Positive range <>) of Internal_Value;

   function As_Boolean (Self : Internal_Value) return Boolean;
   function Create_Boolean (Value : Boolean) return Internal_Value is
     ((Kind => Boolean_Value, Boolean_Value => Value));

   function As_Integer (Self : Internal_Value) return Integer;
   function Create_Integer (Value : Integer) return Internal_Value is
     ((Kind => Integer_Value, Integer_Value => Value));

   function As_Character (Self : Internal_Value) return Character_Type;
   function Create_Character (Value : Character_Type) return Internal_Value is
     ((Kind => Character_Value, Character_Value => Value));

   function As_String (Self : Internal_Value) return String_Type;
   function Create_String (Value : String_Type) return Internal_Value is
     ((Kind => String_Value, String_Value => Value));

   function As_Node (Self : Internal_Value) return Internal_Entity;
   function Create_Node (Value : Internal_Entity) return Internal_Value is
     ((Kind => Node_Value, Node_Value => Value));

      function As_Analysis_Unit_Kind
        (Self : Internal_Value) return Analysis_Unit_Kind;
      function Create_Analysis_Unit_Kind
        (Value : Analysis_Unit_Kind) return Internal_Value
      is ((Kind => Analysis_Unit_Kind_Value,
           Analysis_Unit_Kind_Value => Value));
      function As_Lookup_Kind
        (Self : Internal_Value) return Lookup_Kind;
      function Create_Lookup_Kind
        (Value : Lookup_Kind) return Internal_Value
      is ((Kind => Lookup_Kind_Value,
           Lookup_Kind_Value => Value));
      function As_Designated_Env_Kind
        (Self : Internal_Value) return Designated_Env_Kind;
      function Create_Designated_Env_Kind
        (Value : Designated_Env_Kind) return Internal_Value
      is ((Kind => Designated_Env_Kind_Value,
           Designated_Env_Kind_Value => Value));
      function As_Grammar_Rule
        (Self : Internal_Value) return Grammar_Rule;
      function Create_Grammar_Rule
        (Value : Grammar_Rule) return Internal_Value
      is ((Kind => Grammar_Rule_Value,
           Grammar_Rule_Value => Value));

   -----------------------
   -- Descriptor tables --
   -----------------------

   type String_Access is access constant String;
   type String_Array is array (Positive range <>) of String_Access;

   ------------------------------
   -- Struct field descriptors --
   ------------------------------

   type Struct_Field_Descriptor (Name_Length : Natural) is record
      Reference : Struct_Field_Reference;
      --  Enum value that designates this field

      Field_Type : Type_Constraint;
      --  Type for this field

      Name : String (1 .. Name_Length);
      --  Lower-case name for this field
   end record;
   --  General description of a struct field

   type Struct_Field_Descriptor_Access is
      access constant Struct_Field_Descriptor;
   type Struct_Field_Descriptor_Array is
      array (Positive range <>) of Struct_Field_Descriptor_Access;

   -----------------------------
   -- Struct type descriptors --
   -----------------------------

   type Struct_Type_Descriptor (Fields_Count : Natural) is record
      Fields : Struct_Field_Descriptor_Array (1 .. Fields_Count);
   end record;

   type Struct_Type_Descriptor_Access is
      access constant Struct_Type_Descriptor;

   ------------------------------
   -- Syntax field descriptors --
   ------------------------------

   type Syntax_Field_Descriptor (Name_Length : Natural) is record
      Field_Type : Node_Type_Id;
      Name       : String (1 .. Name_Length);
   end record;
   --  General description of a field (independent of field implementations)

   type Syntax_Field_Descriptor_Access is
      access constant Syntax_Field_Descriptor;

   --  Descriptors for syntax fields

      
      Desc_For_I_D_F_Package : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 9,
            Field_Type  => Common.Unqualified_I_D_Type_Id,
            Name        => "f_package"
         );
      
      Desc_For_I_D_F_Name : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 6,
            Field_Type  => Common.Unqualified_I_D_Type_Id,
            Name        => "f_name"
         );
      
      Desc_For_Aspect_F_Identifier : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 12,
            Field_Type  => Common.Unqualified_I_D_Type_Id,
            Name        => "f_identifier"
         );
      
      Desc_For_Aspect_F_Value : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 7,
            Field_Type  => Common.Expr_Type_Id,
            Name        => "f_value"
         );
      
      Desc_For_Message_Aggregate_Associations_F_Associations : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 14,
            Field_Type  => Common.Message_Aggregate_Association_List_Type_Id,
            Name        => "f_associations"
         );
      
      Desc_For_Checksum_Val_F_Data : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 6,
            Field_Type  => Common.Expr_Type_Id,
            Name        => "f_data"
         );
      
      Desc_For_Checksum_Value_Range_F_First : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 7,
            Field_Type  => Common.Expr_Type_Id,
            Name        => "f_first"
         );
      
      Desc_For_Checksum_Value_Range_F_Last : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 6,
            Field_Type  => Common.Expr_Type_Id,
            Name        => "f_last"
         );
      
      Desc_For_Checksum_Assoc_F_Identifier : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 12,
            Field_Type  => Common.Unqualified_I_D_Type_Id,
            Name        => "f_identifier"
         );
      
      Desc_For_Checksum_Assoc_F_Covered_Fields : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 16,
            Field_Type  => Common.Base_Checksum_Val_List_Type_Id,
            Name        => "f_covered_fields"
         );
      
      Desc_For_Refinement_Decl_F_Pdu : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 5,
            Field_Type  => Common.I_D_Type_Id,
            Name        => "f_pdu"
         );
      
      Desc_For_Refinement_Decl_F_Field : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 7,
            Field_Type  => Common.Unqualified_I_D_Type_Id,
            Name        => "f_field"
         );
      
      Desc_For_Refinement_Decl_F_Sdu : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 5,
            Field_Type  => Common.I_D_Type_Id,
            Name        => "f_sdu"
         );
      
      Desc_For_Refinement_Decl_F_Condition : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 11,
            Field_Type  => Common.Expr_Type_Id,
            Name        => "f_condition"
         );
      
      Desc_For_Session_Decl_F_Parameters : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 12,
            Field_Type  => Common.Formal_Decl_List_Type_Id,
            Name        => "f_parameters"
         );
      
      Desc_For_Session_Decl_F_Identifier : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 12,
            Field_Type  => Common.Unqualified_I_D_Type_Id,
            Name        => "f_identifier"
         );
      
      Desc_For_Session_Decl_F_Declarations : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 14,
            Field_Type  => Common.Local_Decl_List_Type_Id,
            Name        => "f_declarations"
         );
      
      Desc_For_Session_Decl_F_States : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 8,
            Field_Type  => Common.State_List_Type_Id,
            Name        => "f_states"
         );
      
      Desc_For_Session_Decl_F_End_Identifier : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 16,
            Field_Type  => Common.Unqualified_I_D_Type_Id,
            Name        => "f_end_identifier"
         );
      
      Desc_For_Type_Decl_F_Identifier : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 12,
            Field_Type  => Common.Unqualified_I_D_Type_Id,
            Name        => "f_identifier"
         );
      
      Desc_For_Type_Decl_F_Parameters : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 12,
            Field_Type  => Common.Parameters_Type_Id,
            Name        => "f_parameters"
         );
      
      Desc_For_Type_Decl_F_Definition : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 12,
            Field_Type  => Common.Type_Def_Type_Id,
            Name        => "f_definition"
         );
      
      Desc_For_Description_F_Content : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 9,
            Field_Type  => Common.String_Literal_Type_Id,
            Name        => "f_content"
         );
      
      Desc_For_Element_Value_Assoc_F_Identifier : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 12,
            Field_Type  => Common.Unqualified_I_D_Type_Id,
            Name        => "f_identifier"
         );
      
      Desc_For_Element_Value_Assoc_F_Literal : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 9,
            Field_Type  => Common.Numeric_Literal_Type_Id,
            Name        => "f_literal"
         );
      
      Desc_For_Attribute_F_Expression : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 12,
            Field_Type  => Common.Expr_Type_Id,
            Name        => "f_expression"
         );
      
      Desc_For_Attribute_F_Kind : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 6,
            Field_Type  => Common.Attr_Type_Id,
            Name        => "f_kind"
         );
      
      Desc_For_Bin_Op_F_Left : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 6,
            Field_Type  => Common.Expr_Type_Id,
            Name        => "f_left"
         );
      
      Desc_For_Bin_Op_F_Op : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 4,
            Field_Type  => Common.Op_Type_Id,
            Name        => "f_op"
         );
      
      Desc_For_Bin_Op_F_Right : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 7,
            Field_Type  => Common.Expr_Type_Id,
            Name        => "f_right"
         );
      
      Desc_For_Binding_F_Expression : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 12,
            Field_Type  => Common.Expr_Type_Id,
            Name        => "f_expression"
         );
      
      Desc_For_Binding_F_Bindings : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 10,
            Field_Type  => Common.Term_Assoc_List_Type_Id,
            Name        => "f_bindings"
         );
      
      Desc_For_Call_F_Identifier : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 12,
            Field_Type  => Common.Unqualified_I_D_Type_Id,
            Name        => "f_identifier"
         );
      
      Desc_For_Call_F_Arguments : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 11,
            Field_Type  => Common.Expr_List_Type_Id,
            Name        => "f_arguments"
         );
      
      Desc_For_Case_Expression_F_Expression : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 12,
            Field_Type  => Common.Expr_Type_Id,
            Name        => "f_expression"
         );
      
      Desc_For_Case_Expression_F_Choices : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 9,
            Field_Type  => Common.Choice_List_Type_Id,
            Name        => "f_choices"
         );
      
      Desc_For_Choice_F_Selectors : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 11,
            Field_Type  => Common.R_F_L_X_Node_List_Type_Id,
            Name        => "f_selectors"
         );
      
      Desc_For_Choice_F_Expression : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 12,
            Field_Type  => Common.Expr_Type_Id,
            Name        => "f_expression"
         );
      
      Desc_For_Comprehension_F_Iterator : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 10,
            Field_Type  => Common.Unqualified_I_D_Type_Id,
            Name        => "f_iterator"
         );
      
      Desc_For_Comprehension_F_Sequence : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 10,
            Field_Type  => Common.Expr_Type_Id,
            Name        => "f_sequence"
         );
      
      Desc_For_Comprehension_F_Condition : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 11,
            Field_Type  => Common.Expr_Type_Id,
            Name        => "f_condition"
         );
      
      Desc_For_Comprehension_F_Selector : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 10,
            Field_Type  => Common.Expr_Type_Id,
            Name        => "f_selector"
         );
      
      Desc_For_Context_Item_F_Item : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 6,
            Field_Type  => Common.Unqualified_I_D_Type_Id,
            Name        => "f_item"
         );
      
      Desc_For_Conversion_F_Target_Identifier : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 19,
            Field_Type  => Common.I_D_Type_Id,
            Name        => "f_target_identifier"
         );
      
      Desc_For_Conversion_F_Argument : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 10,
            Field_Type  => Common.Expr_Type_Id,
            Name        => "f_argument"
         );
      
      Desc_For_Message_Aggregate_F_Identifier : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 12,
            Field_Type  => Common.I_D_Type_Id,
            Name        => "f_identifier"
         );
      
      Desc_For_Message_Aggregate_F_Values : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 8,
            Field_Type  => Common.Base_Aggregate_Type_Id,
            Name        => "f_values"
         );
      
      Desc_For_Negation_F_Data : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 6,
            Field_Type  => Common.Expr_Type_Id,
            Name        => "f_data"
         );
      
      Desc_For_Paren_Expression_F_Data : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 6,
            Field_Type  => Common.Expr_Type_Id,
            Name        => "f_data"
         );
      
      Desc_For_Quantified_Expression_F_Operation : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 11,
            Field_Type  => Common.Quantifier_Type_Id,
            Name        => "f_operation"
         );
      
      Desc_For_Quantified_Expression_F_Parameter_Identifier : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 22,
            Field_Type  => Common.Unqualified_I_D_Type_Id,
            Name        => "f_parameter_identifier"
         );
      
      Desc_For_Quantified_Expression_F_Iterable : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 10,
            Field_Type  => Common.Expr_Type_Id,
            Name        => "f_iterable"
         );
      
      Desc_For_Quantified_Expression_F_Predicate : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 11,
            Field_Type  => Common.Expr_Type_Id,
            Name        => "f_predicate"
         );
      
      Desc_For_Select_Node_F_Expression : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 12,
            Field_Type  => Common.Expr_Type_Id,
            Name        => "f_expression"
         );
      
      Desc_For_Select_Node_F_Selector : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 10,
            Field_Type  => Common.Unqualified_I_D_Type_Id,
            Name        => "f_selector"
         );
      
      Desc_For_Concatenation_F_Left : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 6,
            Field_Type  => Common.Sequence_Literal_Type_Id,
            Name        => "f_left"
         );
      
      Desc_For_Concatenation_F_Right : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 7,
            Field_Type  => Common.Sequence_Literal_Type_Id,
            Name        => "f_right"
         );
      
      Desc_For_Sequence_Aggregate_F_Values : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 8,
            Field_Type  => Common.Numeric_Literal_List_Type_Id,
            Name        => "f_values"
         );
      
      Desc_For_Variable_F_Identifier : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 12,
            Field_Type  => Common.I_D_Type_Id,
            Name        => "f_identifier"
         );
      
      Desc_For_Formal_Channel_Decl_F_Identifier : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 12,
            Field_Type  => Common.Unqualified_I_D_Type_Id,
            Name        => "f_identifier"
         );
      
      Desc_For_Formal_Channel_Decl_F_Parameters : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 12,
            Field_Type  => Common.Channel_Attribute_List_Type_Id,
            Name        => "f_parameters"
         );
      
      Desc_For_Formal_Function_Decl_F_Identifier : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 12,
            Field_Type  => Common.Unqualified_I_D_Type_Id,
            Name        => "f_identifier"
         );
      
      Desc_For_Formal_Function_Decl_F_Parameters : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 12,
            Field_Type  => Common.Parameters_Type_Id,
            Name        => "f_parameters"
         );
      
      Desc_For_Formal_Function_Decl_F_Return_Type_Identifier : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 24,
            Field_Type  => Common.I_D_Type_Id,
            Name        => "f_return_type_identifier"
         );
      
      Desc_For_Renaming_Decl_F_Identifier : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 12,
            Field_Type  => Common.Unqualified_I_D_Type_Id,
            Name        => "f_identifier"
         );
      
      Desc_For_Renaming_Decl_F_Type_Identifier : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 17,
            Field_Type  => Common.I_D_Type_Id,
            Name        => "f_type_identifier"
         );
      
      Desc_For_Renaming_Decl_F_Expression : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 12,
            Field_Type  => Common.Expr_Type_Id,
            Name        => "f_expression"
         );
      
      Desc_For_Variable_Decl_F_Identifier : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 12,
            Field_Type  => Common.Unqualified_I_D_Type_Id,
            Name        => "f_identifier"
         );
      
      Desc_For_Variable_Decl_F_Type_Identifier : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 17,
            Field_Type  => Common.I_D_Type_Id,
            Name        => "f_type_identifier"
         );
      
      Desc_For_Variable_Decl_F_Initializer : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 13,
            Field_Type  => Common.Expr_Type_Id,
            Name        => "f_initializer"
         );
      
      Desc_For_Message_Aggregate_Association_F_Identifier : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 12,
            Field_Type  => Common.Unqualified_I_D_Type_Id,
            Name        => "f_identifier"
         );
      
      Desc_For_Message_Aggregate_Association_F_Expression : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 12,
            Field_Type  => Common.Expr_Type_Id,
            Name        => "f_expression"
         );
      
      Desc_For_Byte_Order_Aspect_F_Byte_Order : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 12,
            Field_Type  => Common.Byte_Order_Type_Type_Id,
            Name        => "f_byte_order"
         );
      
      Desc_For_Checksum_Aspect_F_Associations : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 14,
            Field_Type  => Common.Checksum_Assoc_List_Type_Id,
            Name        => "f_associations"
         );
      
      Desc_For_Message_Field_F_Identifier : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 12,
            Field_Type  => Common.Unqualified_I_D_Type_Id,
            Name        => "f_identifier"
         );
      
      Desc_For_Message_Field_F_Type_Identifier : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 17,
            Field_Type  => Common.I_D_Type_Id,
            Name        => "f_type_identifier"
         );
      
      Desc_For_Message_Field_F_Type_Arguments : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 16,
            Field_Type  => Common.Type_Argument_List_Type_Id,
            Name        => "f_type_arguments"
         );
      
      Desc_For_Message_Field_F_Aspects : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 9,
            Field_Type  => Common.Aspect_List_Type_Id,
            Name        => "f_aspects"
         );
      
      Desc_For_Message_Field_F_Condition : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 11,
            Field_Type  => Common.Expr_Type_Id,
            Name        => "f_condition"
         );
      
      Desc_For_Message_Field_F_Thens : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 7,
            Field_Type  => Common.Then_Node_List_Type_Id,
            Name        => "f_thens"
         );
      
      Desc_For_Message_Fields_F_Initial_Field : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 15,
            Field_Type  => Common.Null_Message_Field_Type_Id,
            Name        => "f_initial_field"
         );
      
      Desc_For_Message_Fields_F_Fields : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 8,
            Field_Type  => Common.Message_Field_List_Type_Id,
            Name        => "f_fields"
         );
      
      Desc_For_Null_Message_Field_F_Then : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 6,
            Field_Type  => Common.Then_Node_Type_Id,
            Name        => "f_then"
         );
      
      Desc_For_Package_Node_F_Identifier : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 12,
            Field_Type  => Common.Unqualified_I_D_Type_Id,
            Name        => "f_identifier"
         );
      
      Desc_For_Package_Node_F_Declarations : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 14,
            Field_Type  => Common.Declaration_List_Type_Id,
            Name        => "f_declarations"
         );
      
      Desc_For_Package_Node_F_End_Identifier : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 16,
            Field_Type  => Common.Unqualified_I_D_Type_Id,
            Name        => "f_end_identifier"
         );
      
      Desc_For_Parameter_F_Identifier : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 12,
            Field_Type  => Common.Unqualified_I_D_Type_Id,
            Name        => "f_identifier"
         );
      
      Desc_For_Parameter_F_Type_Identifier : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 17,
            Field_Type  => Common.I_D_Type_Id,
            Name        => "f_type_identifier"
         );
      
      Desc_For_Parameters_F_Parameters : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 12,
            Field_Type  => Common.Parameter_List_Type_Id,
            Name        => "f_parameters"
         );
      
      Desc_For_Specification_F_Context_Clause : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 16,
            Field_Type  => Common.Context_Item_List_Type_Id,
            Name        => "f_context_clause"
         );
      
      Desc_For_Specification_F_Package_Declaration : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 21,
            Field_Type  => Common.Package_Node_Type_Id,
            Name        => "f_package_declaration"
         );
      
      Desc_For_State_F_Identifier : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 12,
            Field_Type  => Common.Unqualified_I_D_Type_Id,
            Name        => "f_identifier"
         );
      
      Desc_For_State_F_Description : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 13,
            Field_Type  => Common.Description_Type_Id,
            Name        => "f_description"
         );
      
      Desc_For_State_F_Body : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 6,
            Field_Type  => Common.State_Body_Type_Id,
            Name        => "f_body"
         );
      
      Desc_For_State_Body_F_Declarations : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 14,
            Field_Type  => Common.Local_Decl_List_Type_Id,
            Name        => "f_declarations"
         );
      
      Desc_For_State_Body_F_Actions : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 9,
            Field_Type  => Common.Statement_List_Type_Id,
            Name        => "f_actions"
         );
      
      Desc_For_State_Body_F_Conditional_Transitions : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 25,
            Field_Type  => Common.Conditional_Transition_List_Type_Id,
            Name        => "f_conditional_transitions"
         );
      
      Desc_For_State_Body_F_Final_Transition : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 18,
            Field_Type  => Common.Transition_Type_Id,
            Name        => "f_final_transition"
         );
      
      Desc_For_State_Body_F_Exception_Transition : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 22,
            Field_Type  => Common.Transition_Type_Id,
            Name        => "f_exception_transition"
         );
      
      Desc_For_State_Body_F_End_Identifier : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 16,
            Field_Type  => Common.Unqualified_I_D_Type_Id,
            Name        => "f_end_identifier"
         );
      
      Desc_For_Assignment_F_Identifier : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 12,
            Field_Type  => Common.Unqualified_I_D_Type_Id,
            Name        => "f_identifier"
         );
      
      Desc_For_Assignment_F_Expression : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 12,
            Field_Type  => Common.Expr_Type_Id,
            Name        => "f_expression"
         );
      
      Desc_For_Attribute_Statement_F_Identifier : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 12,
            Field_Type  => Common.Unqualified_I_D_Type_Id,
            Name        => "f_identifier"
         );
      
      Desc_For_Attribute_Statement_F_Attr : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 6,
            Field_Type  => Common.Attr_Stmt_Type_Id,
            Name        => "f_attr"
         );
      
      Desc_For_Attribute_Statement_F_Expression : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 12,
            Field_Type  => Common.Expr_Type_Id,
            Name        => "f_expression"
         );
      
      Desc_For_Message_Field_Assignment_F_Message : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 9,
            Field_Type  => Common.Unqualified_I_D_Type_Id,
            Name        => "f_message"
         );
      
      Desc_For_Message_Field_Assignment_F_Field : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 7,
            Field_Type  => Common.Unqualified_I_D_Type_Id,
            Name        => "f_field"
         );
      
      Desc_For_Message_Field_Assignment_F_Expression : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 12,
            Field_Type  => Common.Expr_Type_Id,
            Name        => "f_expression"
         );
      
      Desc_For_Reset_F_Identifier : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 12,
            Field_Type  => Common.Unqualified_I_D_Type_Id,
            Name        => "f_identifier"
         );
      
      Desc_For_Reset_F_Associations : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 14,
            Field_Type  => Common.Message_Aggregate_Association_List_Type_Id,
            Name        => "f_associations"
         );
      
      Desc_For_Term_Assoc_F_Identifier : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 12,
            Field_Type  => Common.Unqualified_I_D_Type_Id,
            Name        => "f_identifier"
         );
      
      Desc_For_Term_Assoc_F_Expression : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 12,
            Field_Type  => Common.Expr_Type_Id,
            Name        => "f_expression"
         );
      
      Desc_For_Then_Node_F_Target : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 8,
            Field_Type  => Common.Unqualified_I_D_Type_Id,
            Name        => "f_target"
         );
      
      Desc_For_Then_Node_F_Aspects : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 9,
            Field_Type  => Common.Aspect_List_Type_Id,
            Name        => "f_aspects"
         );
      
      Desc_For_Then_Node_F_Condition : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 11,
            Field_Type  => Common.Expr_Type_Id,
            Name        => "f_condition"
         );
      
      Desc_For_Transition_F_Target : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 8,
            Field_Type  => Common.Unqualified_I_D_Type_Id,
            Name        => "f_target"
         );
      
      Desc_For_Transition_F_Description : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 13,
            Field_Type  => Common.Description_Type_Id,
            Name        => "f_description"
         );
      
      Desc_For_Conditional_Transition_F_Condition : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 11,
            Field_Type  => Common.Expr_Type_Id,
            Name        => "f_condition"
         );
      
      Desc_For_Type_Argument_F_Identifier : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 12,
            Field_Type  => Common.Unqualified_I_D_Type_Id,
            Name        => "f_identifier"
         );
      
      Desc_For_Type_Argument_F_Expression : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 12,
            Field_Type  => Common.Expr_Type_Id,
            Name        => "f_expression"
         );
      
      Desc_For_Message_Type_Def_F_Message_Fields : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 16,
            Field_Type  => Common.Message_Fields_Type_Id,
            Name        => "f_message_fields"
         );
      
      Desc_For_Message_Type_Def_F_Aspects : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 9,
            Field_Type  => Common.Message_Aspect_List_Type_Id,
            Name        => "f_aspects"
         );
      
      Desc_For_Named_Enumeration_Def_F_Elements : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 10,
            Field_Type  => Common.Element_Value_Assoc_List_Type_Id,
            Name        => "f_elements"
         );
      
      Desc_For_Positional_Enumeration_Def_F_Elements : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 10,
            Field_Type  => Common.Unqualified_I_D_List_Type_Id,
            Name        => "f_elements"
         );
      
      Desc_For_Enumeration_Type_Def_F_Elements : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 10,
            Field_Type  => Common.Enumeration_Def_Type_Id,
            Name        => "f_elements"
         );
      
      Desc_For_Enumeration_Type_Def_F_Aspects : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 9,
            Field_Type  => Common.Aspect_List_Type_Id,
            Name        => "f_aspects"
         );
      
      Desc_For_Modular_Type_Def_F_Mod : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 5,
            Field_Type  => Common.Expr_Type_Id,
            Name        => "f_mod"
         );
      
      Desc_For_Range_Type_Def_F_First : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 7,
            Field_Type  => Common.Expr_Type_Id,
            Name        => "f_first"
         );
      
      Desc_For_Range_Type_Def_F_Last : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 6,
            Field_Type  => Common.Expr_Type_Id,
            Name        => "f_last"
         );
      
      Desc_For_Range_Type_Def_F_Size : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 6,
            Field_Type  => Common.Aspect_Type_Id,
            Name        => "f_size"
         );
      
      Desc_For_Sequence_Type_Def_F_Element_Type : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 14,
            Field_Type  => Common.I_D_Type_Id,
            Name        => "f_element_type"
         );
      
      Desc_For_Type_Derivation_Def_F_Base : aliased constant
         Syntax_Field_Descriptor := (
            Name_Length => 6,
            Field_Type  => Common.I_D_Type_Id,
            Name        => "f_base"
         );

   Syntax_Field_Descriptors : constant
      array (Syntax_Field_Reference) of Syntax_Field_Descriptor_Access := (
         I_D_F_Package => Desc_For_I_D_F_Package'Access, I_D_F_Name => Desc_For_I_D_F_Name'Access, Aspect_F_Identifier => Desc_For_Aspect_F_Identifier'Access, Aspect_F_Value => Desc_For_Aspect_F_Value'Access, Message_Aggregate_Associations_F_Associations => Desc_For_Message_Aggregate_Associations_F_Associations'Access, Checksum_Val_F_Data => Desc_For_Checksum_Val_F_Data'Access, Checksum_Value_Range_F_First => Desc_For_Checksum_Value_Range_F_First'Access, Checksum_Value_Range_F_Last => Desc_For_Checksum_Value_Range_F_Last'Access, Checksum_Assoc_F_Identifier => Desc_For_Checksum_Assoc_F_Identifier'Access, Checksum_Assoc_F_Covered_Fields => Desc_For_Checksum_Assoc_F_Covered_Fields'Access, Refinement_Decl_F_Pdu => Desc_For_Refinement_Decl_F_Pdu'Access, Refinement_Decl_F_Field => Desc_For_Refinement_Decl_F_Field'Access, Refinement_Decl_F_Sdu => Desc_For_Refinement_Decl_F_Sdu'Access, Refinement_Decl_F_Condition => Desc_For_Refinement_Decl_F_Condition'Access, Session_Decl_F_Parameters => Desc_For_Session_Decl_F_Parameters'Access, Session_Decl_F_Identifier => Desc_For_Session_Decl_F_Identifier'Access, Session_Decl_F_Declarations => Desc_For_Session_Decl_F_Declarations'Access, Session_Decl_F_States => Desc_For_Session_Decl_F_States'Access, Session_Decl_F_End_Identifier => Desc_For_Session_Decl_F_End_Identifier'Access, Type_Decl_F_Identifier => Desc_For_Type_Decl_F_Identifier'Access, Type_Decl_F_Parameters => Desc_For_Type_Decl_F_Parameters'Access, Type_Decl_F_Definition => Desc_For_Type_Decl_F_Definition'Access, Description_F_Content => Desc_For_Description_F_Content'Access, Element_Value_Assoc_F_Identifier => Desc_For_Element_Value_Assoc_F_Identifier'Access, Element_Value_Assoc_F_Literal => Desc_For_Element_Value_Assoc_F_Literal'Access, Attribute_F_Expression => Desc_For_Attribute_F_Expression'Access, Attribute_F_Kind => Desc_For_Attribute_F_Kind'Access, Bin_Op_F_Left => Desc_For_Bin_Op_F_Left'Access, Bin_Op_F_Op => Desc_For_Bin_Op_F_Op'Access, Bin_Op_F_Right => Desc_For_Bin_Op_F_Right'Access, Binding_F_Expression => Desc_For_Binding_F_Expression'Access, Binding_F_Bindings => Desc_For_Binding_F_Bindings'Access, Call_F_Identifier => Desc_For_Call_F_Identifier'Access, Call_F_Arguments => Desc_For_Call_F_Arguments'Access, Case_Expression_F_Expression => Desc_For_Case_Expression_F_Expression'Access, Case_Expression_F_Choices => Desc_For_Case_Expression_F_Choices'Access, Choice_F_Selectors => Desc_For_Choice_F_Selectors'Access, Choice_F_Expression => Desc_For_Choice_F_Expression'Access, Comprehension_F_Iterator => Desc_For_Comprehension_F_Iterator'Access, Comprehension_F_Sequence => Desc_For_Comprehension_F_Sequence'Access, Comprehension_F_Condition => Desc_For_Comprehension_F_Condition'Access, Comprehension_F_Selector => Desc_For_Comprehension_F_Selector'Access, Context_Item_F_Item => Desc_For_Context_Item_F_Item'Access, Conversion_F_Target_Identifier => Desc_For_Conversion_F_Target_Identifier'Access, Conversion_F_Argument => Desc_For_Conversion_F_Argument'Access, Message_Aggregate_F_Identifier => Desc_For_Message_Aggregate_F_Identifier'Access, Message_Aggregate_F_Values => Desc_For_Message_Aggregate_F_Values'Access, Negation_F_Data => Desc_For_Negation_F_Data'Access, Paren_Expression_F_Data => Desc_For_Paren_Expression_F_Data'Access, Quantified_Expression_F_Operation => Desc_For_Quantified_Expression_F_Operation'Access, Quantified_Expression_F_Parameter_Identifier => Desc_For_Quantified_Expression_F_Parameter_Identifier'Access, Quantified_Expression_F_Iterable => Desc_For_Quantified_Expression_F_Iterable'Access, Quantified_Expression_F_Predicate => Desc_For_Quantified_Expression_F_Predicate'Access, Select_Node_F_Expression => Desc_For_Select_Node_F_Expression'Access, Select_Node_F_Selector => Desc_For_Select_Node_F_Selector'Access, Concatenation_F_Left => Desc_For_Concatenation_F_Left'Access, Concatenation_F_Right => Desc_For_Concatenation_F_Right'Access, Sequence_Aggregate_F_Values => Desc_For_Sequence_Aggregate_F_Values'Access, Variable_F_Identifier => Desc_For_Variable_F_Identifier'Access, Formal_Channel_Decl_F_Identifier => Desc_For_Formal_Channel_Decl_F_Identifier'Access, Formal_Channel_Decl_F_Parameters => Desc_For_Formal_Channel_Decl_F_Parameters'Access, Formal_Function_Decl_F_Identifier => Desc_For_Formal_Function_Decl_F_Identifier'Access, Formal_Function_Decl_F_Parameters => Desc_For_Formal_Function_Decl_F_Parameters'Access, Formal_Function_Decl_F_Return_Type_Identifier => Desc_For_Formal_Function_Decl_F_Return_Type_Identifier'Access, Renaming_Decl_F_Identifier => Desc_For_Renaming_Decl_F_Identifier'Access, Renaming_Decl_F_Type_Identifier => Desc_For_Renaming_Decl_F_Type_Identifier'Access, Renaming_Decl_F_Expression => Desc_For_Renaming_Decl_F_Expression'Access, Variable_Decl_F_Identifier => Desc_For_Variable_Decl_F_Identifier'Access, Variable_Decl_F_Type_Identifier => Desc_For_Variable_Decl_F_Type_Identifier'Access, Variable_Decl_F_Initializer => Desc_For_Variable_Decl_F_Initializer'Access, Message_Aggregate_Association_F_Identifier => Desc_For_Message_Aggregate_Association_F_Identifier'Access, Message_Aggregate_Association_F_Expression => Desc_For_Message_Aggregate_Association_F_Expression'Access, Byte_Order_Aspect_F_Byte_Order => Desc_For_Byte_Order_Aspect_F_Byte_Order'Access, Checksum_Aspect_F_Associations => Desc_For_Checksum_Aspect_F_Associations'Access, Message_Field_F_Identifier => Desc_For_Message_Field_F_Identifier'Access, Message_Field_F_Type_Identifier => Desc_For_Message_Field_F_Type_Identifier'Access, Message_Field_F_Type_Arguments => Desc_For_Message_Field_F_Type_Arguments'Access, Message_Field_F_Aspects => Desc_For_Message_Field_F_Aspects'Access, Message_Field_F_Condition => Desc_For_Message_Field_F_Condition'Access, Message_Field_F_Thens => Desc_For_Message_Field_F_Thens'Access, Message_Fields_F_Initial_Field => Desc_For_Message_Fields_F_Initial_Field'Access, Message_Fields_F_Fields => Desc_For_Message_Fields_F_Fields'Access, Null_Message_Field_F_Then => Desc_For_Null_Message_Field_F_Then'Access, Package_Node_F_Identifier => Desc_For_Package_Node_F_Identifier'Access, Package_Node_F_Declarations => Desc_For_Package_Node_F_Declarations'Access, Package_Node_F_End_Identifier => Desc_For_Package_Node_F_End_Identifier'Access, Parameter_F_Identifier => Desc_For_Parameter_F_Identifier'Access, Parameter_F_Type_Identifier => Desc_For_Parameter_F_Type_Identifier'Access, Parameters_F_Parameters => Desc_For_Parameters_F_Parameters'Access, Specification_F_Context_Clause => Desc_For_Specification_F_Context_Clause'Access, Specification_F_Package_Declaration => Desc_For_Specification_F_Package_Declaration'Access, State_F_Identifier => Desc_For_State_F_Identifier'Access, State_F_Description => Desc_For_State_F_Description'Access, State_F_Body => Desc_For_State_F_Body'Access, State_Body_F_Declarations => Desc_For_State_Body_F_Declarations'Access, State_Body_F_Actions => Desc_For_State_Body_F_Actions'Access, State_Body_F_Conditional_Transitions => Desc_For_State_Body_F_Conditional_Transitions'Access, State_Body_F_Final_Transition => Desc_For_State_Body_F_Final_Transition'Access, State_Body_F_Exception_Transition => Desc_For_State_Body_F_Exception_Transition'Access, State_Body_F_End_Identifier => Desc_For_State_Body_F_End_Identifier'Access, Assignment_F_Identifier => Desc_For_Assignment_F_Identifier'Access, Assignment_F_Expression => Desc_For_Assignment_F_Expression'Access, Attribute_Statement_F_Identifier => Desc_For_Attribute_Statement_F_Identifier'Access, Attribute_Statement_F_Attr => Desc_For_Attribute_Statement_F_Attr'Access, Attribute_Statement_F_Expression => Desc_For_Attribute_Statement_F_Expression'Access, Message_Field_Assignment_F_Message => Desc_For_Message_Field_Assignment_F_Message'Access, Message_Field_Assignment_F_Field => Desc_For_Message_Field_Assignment_F_Field'Access, Message_Field_Assignment_F_Expression => Desc_For_Message_Field_Assignment_F_Expression'Access, Reset_F_Identifier => Desc_For_Reset_F_Identifier'Access, Reset_F_Associations => Desc_For_Reset_F_Associations'Access, Term_Assoc_F_Identifier => Desc_For_Term_Assoc_F_Identifier'Access, Term_Assoc_F_Expression => Desc_For_Term_Assoc_F_Expression'Access, Then_Node_F_Target => Desc_For_Then_Node_F_Target'Access, Then_Node_F_Aspects => Desc_For_Then_Node_F_Aspects'Access, Then_Node_F_Condition => Desc_For_Then_Node_F_Condition'Access, Transition_F_Target => Desc_For_Transition_F_Target'Access, Transition_F_Description => Desc_For_Transition_F_Description'Access, Conditional_Transition_F_Condition => Desc_For_Conditional_Transition_F_Condition'Access, Type_Argument_F_Identifier => Desc_For_Type_Argument_F_Identifier'Access, Type_Argument_F_Expression => Desc_For_Type_Argument_F_Expression'Access, Message_Type_Def_F_Message_Fields => Desc_For_Message_Type_Def_F_Message_Fields'Access, Message_Type_Def_F_Aspects => Desc_For_Message_Type_Def_F_Aspects'Access, Named_Enumeration_Def_F_Elements => Desc_For_Named_Enumeration_Def_F_Elements'Access, Positional_Enumeration_Def_F_Elements => Desc_For_Positional_Enumeration_Def_F_Elements'Access, Enumeration_Type_Def_F_Elements => Desc_For_Enumeration_Type_Def_F_Elements'Access, Enumeration_Type_Def_F_Aspects => Desc_For_Enumeration_Type_Def_F_Aspects'Access, Modular_Type_Def_F_Mod => Desc_For_Modular_Type_Def_F_Mod'Access, Range_Type_Def_F_First => Desc_For_Range_Type_Def_F_First'Access, Range_Type_Def_F_Last => Desc_For_Range_Type_Def_F_Last'Access, Range_Type_Def_F_Size => Desc_For_Range_Type_Def_F_Size'Access, Sequence_Type_Def_F_Element_Type => Desc_For_Sequence_Type_Def_F_Element_Type'Access, Type_Derivation_Def_F_Base => Desc_For_Type_Derivation_Def_F_Base'Access
   );

   --------------------------
   -- Property descriptors --
   --------------------------

   type Property_Descriptor (
      Name_Length : Natural;
      --  Length of the proprety name

      Arity : Natural
      --  Number of arguments this property takes (exclude the ``Self``
      --  argument).
   )
   is record
      Name : String (1 .. Name_Length);
      --  Lower-case name for this property

      Return_Type : Type_Constraint;
      --  Return type for this property

      Argument_Types : Type_Constraint_Array (1 .. Arity);
      --  Types of the arguments that this property takes

      Argument_Names : String_Array (1 .. Arity);
      --  Lower-case names for arguments that this property takes

      Argument_Default_Values : Internal_Value_Array (1 .. Arity);
      --  Default values (if any, otherwise ``No_Internal_Value``) for
      --  arguments that this property takes.
   end record;

   type Property_Descriptor_Access is access constant Property_Descriptor;

   --  Descriptors for properties

   
   Name_For_with_self : aliased constant String := "with_self";

      
      Desc_For_R_F_L_X_Node_Parent : aliased constant
         Property_Descriptor := (
            Name_Length => 6,
            Arity       => 0,

            Name => "parent",

            Return_Type    => (Kind => Node_Value, Node_Type => Common.R_F_L_X_Node_Type_Id),
            Argument_Types => (
                  1 .. 0 => <>
            ),
            Argument_Names => (
                  1 .. 0 => <>
            ),
            Argument_Default_Values => (
                  1 .. 0 => <>
            )
         );
      
      Desc_For_R_F_L_X_Node_Parents : aliased constant
         Property_Descriptor := (
            Name_Length => 7,
            Arity       => 1,

            Name => "parents",

            Return_Type    => (Kind => R_F_L_X_Node_Array_Value),
            Argument_Types => (
                  1 => (Kind => Boolean_Value)
            ),
            Argument_Names => (
                  1 => Name_For_with_self'Access
            ),
            Argument_Default_Values => (
                  1 => Create_Boolean (True)
            )
         );
      
      Desc_For_R_F_L_X_Node_Children : aliased constant
         Property_Descriptor := (
            Name_Length => 8,
            Arity       => 0,

            Name => "children",

            Return_Type    => (Kind => R_F_L_X_Node_Array_Value),
            Argument_Types => (
                  1 .. 0 => <>
            ),
            Argument_Names => (
                  1 .. 0 => <>
            ),
            Argument_Default_Values => (
                  1 .. 0 => <>
            )
         );
      
      Desc_For_R_F_L_X_Node_Token_Start : aliased constant
         Property_Descriptor := (
            Name_Length => 11,
            Arity       => 0,

            Name => "token_start",

            Return_Type    => (Kind => Token_Value),
            Argument_Types => (
                  1 .. 0 => <>
            ),
            Argument_Names => (
                  1 .. 0 => <>
            ),
            Argument_Default_Values => (
                  1 .. 0 => <>
            )
         );
      
      Desc_For_R_F_L_X_Node_Token_End : aliased constant
         Property_Descriptor := (
            Name_Length => 9,
            Arity       => 0,

            Name => "token_end",

            Return_Type    => (Kind => Token_Value),
            Argument_Types => (
                  1 .. 0 => <>
            ),
            Argument_Names => (
                  1 .. 0 => <>
            ),
            Argument_Default_Values => (
                  1 .. 0 => <>
            )
         );
      
      Desc_For_R_F_L_X_Node_Child_Index : aliased constant
         Property_Descriptor := (
            Name_Length => 11,
            Arity       => 0,

            Name => "child_index",

            Return_Type    => (Kind => Integer_Value),
            Argument_Types => (
                  1 .. 0 => <>
            ),
            Argument_Names => (
                  1 .. 0 => <>
            ),
            Argument_Default_Values => (
                  1 .. 0 => <>
            )
         );
      
      Desc_For_R_F_L_X_Node_Previous_Sibling : aliased constant
         Property_Descriptor := (
            Name_Length => 16,
            Arity       => 0,

            Name => "previous_sibling",

            Return_Type    => (Kind => Node_Value, Node_Type => Common.R_F_L_X_Node_Type_Id),
            Argument_Types => (
                  1 .. 0 => <>
            ),
            Argument_Names => (
                  1 .. 0 => <>
            ),
            Argument_Default_Values => (
                  1 .. 0 => <>
            )
         );
      
      Desc_For_R_F_L_X_Node_Next_Sibling : aliased constant
         Property_Descriptor := (
            Name_Length => 12,
            Arity       => 0,

            Name => "next_sibling",

            Return_Type    => (Kind => Node_Value, Node_Type => Common.R_F_L_X_Node_Type_Id),
            Argument_Types => (
                  1 .. 0 => <>
            ),
            Argument_Names => (
                  1 .. 0 => <>
            ),
            Argument_Default_Values => (
                  1 .. 0 => <>
            )
         );
      
      Desc_For_R_F_L_X_Node_Unit : aliased constant
         Property_Descriptor := (
            Name_Length => 4,
            Arity       => 0,

            Name => "unit",

            Return_Type    => (Kind => Analysis_Unit_Value),
            Argument_Types => (
                  1 .. 0 => <>
            ),
            Argument_Names => (
                  1 .. 0 => <>
            ),
            Argument_Default_Values => (
                  1 .. 0 => <>
            )
         );
      
      Desc_For_R_F_L_X_Node_Is_Ghost : aliased constant
         Property_Descriptor := (
            Name_Length => 8,
            Arity       => 0,

            Name => "is_ghost",

            Return_Type    => (Kind => Boolean_Value),
            Argument_Types => (
                  1 .. 0 => <>
            ),
            Argument_Names => (
                  1 .. 0 => <>
            ),
            Argument_Default_Values => (
                  1 .. 0 => <>
            )
         );
      
      Desc_For_R_F_L_X_Node_Full_Sloc_Image : aliased constant
         Property_Descriptor := (
            Name_Length => 15,
            Arity       => 0,

            Name => "full_sloc_image",

            Return_Type    => (Kind => String_Value),
            Argument_Types => (
                  1 .. 0 => <>
            ),
            Argument_Names => (
                  1 .. 0 => <>
            ),
            Argument_Default_Values => (
                  1 .. 0 => <>
            )
         );

      Property_Descriptors : constant
         array (Property_Reference) of Property_Descriptor_Access := (
            Desc_For_R_F_L_X_Node_Parent'Access, Desc_For_R_F_L_X_Node_Parents'Access, Desc_For_R_F_L_X_Node_Children'Access, Desc_For_R_F_L_X_Node_Token_Start'Access, Desc_For_R_F_L_X_Node_Token_End'Access, Desc_For_R_F_L_X_Node_Child_Index'Access, Desc_For_R_F_L_X_Node_Previous_Sibling'Access, Desc_For_R_F_L_X_Node_Next_Sibling'Access, Desc_For_R_F_L_X_Node_Unit'Access, Desc_For_R_F_L_X_Node_Is_Ghost'Access, Desc_For_R_F_L_X_Node_Full_Sloc_Image'Access
      );

   ---------------------------
   -- Node type descriptors --
   ---------------------------

   type Node_Field_Descriptor (Is_Abstract_Or_Null : Boolean) is record
      Field : Syntax_Field_Reference;
      --  Reference to the field this describes

      --  Only non-null concrete fields are assigned an index

      case Is_Abstract_Or_Null is
         when False =>
            Index : Positive;
            --  Index for this field

         when True =>
            null;
      end case;
   end record;
   --  Description of a field as implemented by a specific node

   type Node_Field_Descriptor_Access is access constant Node_Field_Descriptor;
   type Node_Field_Descriptor_Array is
      array (Positive range <>) of Node_Field_Descriptor_Access;

   type Node_Type_Descriptor
     (Is_Abstract       : Boolean;
      Derivations_Count : Natural;
      Fields_Count      : Natural;
      Properties_Count  : Natural)
   is record
      Base_Type : Any_Node_Type_Id;
      --  Reference to the node type from which this derives

      Derivations : Node_Type_Id_Array (1 .. Derivations_Count);
      --  List of references for all node types that derives from this

      DSL_Name : Unbounded_String;
      --  Name for this type in the Langkit DSL

      Inherited_Fields : Natural;
      --  Number of syntax field inherited from the base type

      Fields : Node_Field_Descriptor_Array (1 .. Fields_Count);
      --  For regular node types, list of syntax fields that are specific to
      --  this derivation (i.e. excluding fields from the base type).

      Properties : Property_Reference_Array (1 .. Properties_Count);
      --  List of properties that this node provides that are specific to this
      --  derivation (i.e. excluding fields from the base type).

      --  Only concrete nodes are assigned a node kind

      case Is_Abstract is
         when False =>
            Kind : R_F_L_X_Node_Kind_Type;
            --  Kind corresponding this this node type

         when True =>
            null;
      end case;
   end record;

   type Node_Type_Descriptor_Access is access constant Node_Type_Descriptor;

   --  Descriptors for struct types and their fields


   Struct_Field_Descriptors : constant
      array (Struct_Field_Reference) of Struct_Field_Descriptor_Access := (
         Struct_Field_Reference => <>
   );


   --  Descriptors for node types and their syntax fields

   


   Desc_For_R_F_L_X_Node : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => True,
      Derivations_Count => 35,
      Fields_Count      => 0,
      Properties_Count  => 11,

      Base_Type   => None,
      Derivations =>
         (1 => Common.Abstract_I_D_Type_Id, 2 => Common.Aspect_Type_Id, 3 => Common.Attr_Type_Id, 4 => Common.Attr_Stmt_Type_Id, 5 => Common.Base_Aggregate_Type_Id, 6 => Common.Base_Checksum_Val_Type_Id, 7 => Common.Byte_Order_Type_Type_Id, 8 => Common.Channel_Attribute_Type_Id, 9 => Common.Checksum_Assoc_Type_Id, 10 => Common.Declaration_Type_Id, 11 => Common.Description_Type_Id, 12 => Common.Element_Value_Assoc_Type_Id, 13 => Common.Expr_Type_Id, 14 => Common.Formal_Decl_Type_Id, 15 => Common.Local_Decl_Type_Id, 16 => Common.Message_Aggregate_Association_Type_Id, 17 => Common.Message_Aspect_Type_Id, 18 => Common.Message_Field_Type_Id, 19 => Common.Message_Fields_Type_Id, 20 => Common.Null_Message_Field_Type_Id, 21 => Common.Op_Type_Id, 22 => Common.Package_Node_Type_Id, 23 => Common.Parameter_Type_Id, 24 => Common.Parameters_Type_Id, 25 => Common.Quantifier_Type_Id, 26 => Common.R_F_L_X_Node_Base_List_Type_Id, 27 => Common.Specification_Type_Id, 28 => Common.State_Type_Id, 29 => Common.State_Body_Type_Id, 30 => Common.Statement_Type_Id, 31 => Common.Term_Assoc_Type_Id, 32 => Common.Then_Node_Type_Id, 33 => Common.Transition_Type_Id, 34 => Common.Type_Argument_Type_Id, 35 => Common.Type_Def_Type_Id),

      DSL_Name => To_Unbounded_String ("RFLXNode"),

      Inherited_Fields => 0,
      Fields           => (
            1 .. 0 => <>
      ),

      Properties => (
            1 => R_F_L_X_Node_Parent, 2 => R_F_L_X_Node_Parents, 3 => R_F_L_X_Node_Children, 4 => R_F_L_X_Node_Token_Start, 5 => R_F_L_X_Node_Token_End, 6 => R_F_L_X_Node_Child_Index, 7 => R_F_L_X_Node_Previous_Sibling, 8 => R_F_L_X_Node_Next_Sibling, 9 => R_F_L_X_Node_Unit, 10 => R_F_L_X_Node_Is_Ghost, 11 => R_F_L_X_Node_Full_Sloc_Image
      )

   );
   


   Desc_For_Abstract_I_D : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => True,
      Derivations_Count => 2,
      Fields_Count      => 0,
      Properties_Count  => 0,

      Base_Type   => Common.R_F_L_X_Node_Type_Id,
      Derivations =>
         (1 => Common.I_D_Type_Id, 2 => Common.Unqualified_I_D_Type_Id),

      DSL_Name => To_Unbounded_String ("AbstractID"),

      Inherited_Fields => 0,
      Fields           => (
            1 .. 0 => <>
      ),

      Properties => (
            1 .. 0 => <>
      )

   );
   

   I_D_F_Package_For_I_D : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => I_D_F_Package

         , Index => 1
   );
   I_D_F_Name_For_I_D : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => I_D_F_Name

         , Index => 2
   );

   Desc_For_I_D : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 2,
      Properties_Count  => 0,

      Base_Type   => Common.Abstract_I_D_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("ID"),

      Inherited_Fields => 0,
      Fields           => (
            1 => I_D_F_Package_For_I_D'Access, 2 => I_D_F_Name_For_I_D'Access
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_I_D
   );
   


   Desc_For_Unqualified_I_D : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 0,
      Properties_Count  => 0,

      Base_Type   => Common.Abstract_I_D_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("UnqualifiedID"),

      Inherited_Fields => 0,
      Fields           => (
            1 .. 0 => <>
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Unqualified_I_D
   );
   

   Aspect_F_Identifier_For_Aspect : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Aspect_F_Identifier

         , Index => 1
   );
   Aspect_F_Value_For_Aspect : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Aspect_F_Value

         , Index => 2
   );

   Desc_For_Aspect : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 2,
      Properties_Count  => 0,

      Base_Type   => Common.R_F_L_X_Node_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("Aspect"),

      Inherited_Fields => 0,
      Fields           => (
            1 => Aspect_F_Identifier_For_Aspect'Access, 2 => Aspect_F_Value_For_Aspect'Access
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Aspect
   );
   


   Desc_For_Attr : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => True,
      Derivations_Count => 9,
      Fields_Count      => 0,
      Properties_Count  => 0,

      Base_Type   => Common.R_F_L_X_Node_Type_Id,
      Derivations =>
         (1 => Common.Attr_First_Type_Id, 2 => Common.Attr_Has_Data_Type_Id, 3 => Common.Attr_Head_Type_Id, 4 => Common.Attr_Last_Type_Id, 5 => Common.Attr_Opaque_Type_Id, 6 => Common.Attr_Present_Type_Id, 7 => Common.Attr_Size_Type_Id, 8 => Common.Attr_Valid_Type_Id, 9 => Common.Attr_Valid_Checksum_Type_Id),

      DSL_Name => To_Unbounded_String ("Attr"),

      Inherited_Fields => 0,
      Fields           => (
            1 .. 0 => <>
      ),

      Properties => (
            1 .. 0 => <>
      )

   );
   


   Desc_For_Attr_First : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 0,
      Properties_Count  => 0,

      Base_Type   => Common.Attr_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("Attr.First"),

      Inherited_Fields => 0,
      Fields           => (
            1 .. 0 => <>
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Attr_First
   );
   


   Desc_For_Attr_Has_Data : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 0,
      Properties_Count  => 0,

      Base_Type   => Common.Attr_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("Attr.HasData"),

      Inherited_Fields => 0,
      Fields           => (
            1 .. 0 => <>
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Attr_Has_Data
   );
   


   Desc_For_Attr_Head : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 0,
      Properties_Count  => 0,

      Base_Type   => Common.Attr_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("Attr.Head"),

      Inherited_Fields => 0,
      Fields           => (
            1 .. 0 => <>
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Attr_Head
   );
   


   Desc_For_Attr_Last : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 0,
      Properties_Count  => 0,

      Base_Type   => Common.Attr_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("Attr.Last"),

      Inherited_Fields => 0,
      Fields           => (
            1 .. 0 => <>
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Attr_Last
   );
   


   Desc_For_Attr_Opaque : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 0,
      Properties_Count  => 0,

      Base_Type   => Common.Attr_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("Attr.Opaque"),

      Inherited_Fields => 0,
      Fields           => (
            1 .. 0 => <>
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Attr_Opaque
   );
   


   Desc_For_Attr_Present : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 0,
      Properties_Count  => 0,

      Base_Type   => Common.Attr_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("Attr.Present"),

      Inherited_Fields => 0,
      Fields           => (
            1 .. 0 => <>
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Attr_Present
   );
   


   Desc_For_Attr_Size : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 0,
      Properties_Count  => 0,

      Base_Type   => Common.Attr_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("Attr.Size"),

      Inherited_Fields => 0,
      Fields           => (
            1 .. 0 => <>
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Attr_Size
   );
   


   Desc_For_Attr_Valid : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 0,
      Properties_Count  => 0,

      Base_Type   => Common.Attr_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("Attr.Valid"),

      Inherited_Fields => 0,
      Fields           => (
            1 .. 0 => <>
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Attr_Valid
   );
   


   Desc_For_Attr_Valid_Checksum : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 0,
      Properties_Count  => 0,

      Base_Type   => Common.Attr_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("Attr.ValidChecksum"),

      Inherited_Fields => 0,
      Fields           => (
            1 .. 0 => <>
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Attr_Valid_Checksum
   );
   


   Desc_For_Attr_Stmt : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => True,
      Derivations_Count => 4,
      Fields_Count      => 0,
      Properties_Count  => 0,

      Base_Type   => Common.R_F_L_X_Node_Type_Id,
      Derivations =>
         (1 => Common.Attr_Stmt_Append_Type_Id, 2 => Common.Attr_Stmt_Extend_Type_Id, 3 => Common.Attr_Stmt_Read_Type_Id, 4 => Common.Attr_Stmt_Write_Type_Id),

      DSL_Name => To_Unbounded_String ("AttrStmt"),

      Inherited_Fields => 0,
      Fields           => (
            1 .. 0 => <>
      ),

      Properties => (
            1 .. 0 => <>
      )

   );
   


   Desc_For_Attr_Stmt_Append : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 0,
      Properties_Count  => 0,

      Base_Type   => Common.Attr_Stmt_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("AttrStmt.Append"),

      Inherited_Fields => 0,
      Fields           => (
            1 .. 0 => <>
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Attr_Stmt_Append
   );
   


   Desc_For_Attr_Stmt_Extend : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 0,
      Properties_Count  => 0,

      Base_Type   => Common.Attr_Stmt_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("AttrStmt.Extend"),

      Inherited_Fields => 0,
      Fields           => (
            1 .. 0 => <>
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Attr_Stmt_Extend
   );
   


   Desc_For_Attr_Stmt_Read : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 0,
      Properties_Count  => 0,

      Base_Type   => Common.Attr_Stmt_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("AttrStmt.Read"),

      Inherited_Fields => 0,
      Fields           => (
            1 .. 0 => <>
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Attr_Stmt_Read
   );
   


   Desc_For_Attr_Stmt_Write : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 0,
      Properties_Count  => 0,

      Base_Type   => Common.Attr_Stmt_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("AttrStmt.Write"),

      Inherited_Fields => 0,
      Fields           => (
            1 .. 0 => <>
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Attr_Stmt_Write
   );
   


   Desc_For_Base_Aggregate : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => True,
      Derivations_Count => 2,
      Fields_Count      => 0,
      Properties_Count  => 0,

      Base_Type   => Common.R_F_L_X_Node_Type_Id,
      Derivations =>
         (1 => Common.Message_Aggregate_Associations_Type_Id, 2 => Common.Null_Message_Aggregate_Type_Id),

      DSL_Name => To_Unbounded_String ("BaseAggregate"),

      Inherited_Fields => 0,
      Fields           => (
            1 .. 0 => <>
      ),

      Properties => (
            1 .. 0 => <>
      )

   );
   

   Message_Aggregate_Associations_F_Associations_For_Message_Aggregate_Associations : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Message_Aggregate_Associations_F_Associations

         , Index => 1
   );

   Desc_For_Message_Aggregate_Associations : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 1,
      Properties_Count  => 0,

      Base_Type   => Common.Base_Aggregate_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("MessageAggregateAssociations"),

      Inherited_Fields => 0,
      Fields           => (
            1 => Message_Aggregate_Associations_F_Associations_For_Message_Aggregate_Associations'Access
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Message_Aggregate_Associations
   );
   


   Desc_For_Null_Message_Aggregate : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 0,
      Properties_Count  => 0,

      Base_Type   => Common.Base_Aggregate_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("NullMessageAggregate"),

      Inherited_Fields => 0,
      Fields           => (
            1 .. 0 => <>
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Null_Message_Aggregate
   );
   


   Desc_For_Base_Checksum_Val : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => True,
      Derivations_Count => 2,
      Fields_Count      => 0,
      Properties_Count  => 0,

      Base_Type   => Common.R_F_L_X_Node_Type_Id,
      Derivations =>
         (1 => Common.Checksum_Val_Type_Id, 2 => Common.Checksum_Value_Range_Type_Id),

      DSL_Name => To_Unbounded_String ("BaseChecksumVal"),

      Inherited_Fields => 0,
      Fields           => (
            1 .. 0 => <>
      ),

      Properties => (
            1 .. 0 => <>
      )

   );
   

   Checksum_Val_F_Data_For_Checksum_Val : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Checksum_Val_F_Data

         , Index => 1
   );

   Desc_For_Checksum_Val : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 1,
      Properties_Count  => 0,

      Base_Type   => Common.Base_Checksum_Val_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("ChecksumVal"),

      Inherited_Fields => 0,
      Fields           => (
            1 => Checksum_Val_F_Data_For_Checksum_Val'Access
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Checksum_Val
   );
   

   Checksum_Value_Range_F_First_For_Checksum_Value_Range : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Checksum_Value_Range_F_First

         , Index => 1
   );
   Checksum_Value_Range_F_Last_For_Checksum_Value_Range : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Checksum_Value_Range_F_Last

         , Index => 2
   );

   Desc_For_Checksum_Value_Range : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 2,
      Properties_Count  => 0,

      Base_Type   => Common.Base_Checksum_Val_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("ChecksumValueRange"),

      Inherited_Fields => 0,
      Fields           => (
            1 => Checksum_Value_Range_F_First_For_Checksum_Value_Range'Access, 2 => Checksum_Value_Range_F_Last_For_Checksum_Value_Range'Access
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Checksum_Value_Range
   );
   


   Desc_For_Byte_Order_Type : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => True,
      Derivations_Count => 2,
      Fields_Count      => 0,
      Properties_Count  => 0,

      Base_Type   => Common.R_F_L_X_Node_Type_Id,
      Derivations =>
         (1 => Common.Byte_Order_Type_Highorderfirst_Type_Id, 2 => Common.Byte_Order_Type_Loworderfirst_Type_Id),

      DSL_Name => To_Unbounded_String ("ByteOrderType"),

      Inherited_Fields => 0,
      Fields           => (
            1 .. 0 => <>
      ),

      Properties => (
            1 .. 0 => <>
      )

   );
   


   Desc_For_Byte_Order_Type_Highorderfirst : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 0,
      Properties_Count  => 0,

      Base_Type   => Common.Byte_Order_Type_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("ByteOrderType.Highorderfirst"),

      Inherited_Fields => 0,
      Fields           => (
            1 .. 0 => <>
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Byte_Order_Type_Highorderfirst
   );
   


   Desc_For_Byte_Order_Type_Loworderfirst : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 0,
      Properties_Count  => 0,

      Base_Type   => Common.Byte_Order_Type_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("ByteOrderType.Loworderfirst"),

      Inherited_Fields => 0,
      Fields           => (
            1 .. 0 => <>
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Byte_Order_Type_Loworderfirst
   );
   


   Desc_For_Channel_Attribute : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => True,
      Derivations_Count => 2,
      Fields_Count      => 0,
      Properties_Count  => 0,

      Base_Type   => Common.R_F_L_X_Node_Type_Id,
      Derivations =>
         (1 => Common.Readable_Type_Id, 2 => Common.Writable_Type_Id),

      DSL_Name => To_Unbounded_String ("ChannelAttribute"),

      Inherited_Fields => 0,
      Fields           => (
            1 .. 0 => <>
      ),

      Properties => (
            1 .. 0 => <>
      )

   );
   


   Desc_For_Readable : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 0,
      Properties_Count  => 0,

      Base_Type   => Common.Channel_Attribute_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("Readable"),

      Inherited_Fields => 0,
      Fields           => (
            1 .. 0 => <>
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Readable
   );
   


   Desc_For_Writable : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 0,
      Properties_Count  => 0,

      Base_Type   => Common.Channel_Attribute_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("Writable"),

      Inherited_Fields => 0,
      Fields           => (
            1 .. 0 => <>
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Writable
   );
   

   Checksum_Assoc_F_Identifier_For_Checksum_Assoc : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Checksum_Assoc_F_Identifier

         , Index => 1
   );
   Checksum_Assoc_F_Covered_Fields_For_Checksum_Assoc : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Checksum_Assoc_F_Covered_Fields

         , Index => 2
   );

   Desc_For_Checksum_Assoc : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 2,
      Properties_Count  => 0,

      Base_Type   => Common.R_F_L_X_Node_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("ChecksumAssoc"),

      Inherited_Fields => 0,
      Fields           => (
            1 => Checksum_Assoc_F_Identifier_For_Checksum_Assoc'Access, 2 => Checksum_Assoc_F_Covered_Fields_For_Checksum_Assoc'Access
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Checksum_Assoc
   );
   


   Desc_For_Declaration : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => True,
      Derivations_Count => 3,
      Fields_Count      => 0,
      Properties_Count  => 0,

      Base_Type   => Common.R_F_L_X_Node_Type_Id,
      Derivations =>
         (1 => Common.Refinement_Decl_Type_Id, 2 => Common.Session_Decl_Type_Id, 3 => Common.Type_Decl_Type_Id),

      DSL_Name => To_Unbounded_String ("Declaration"),

      Inherited_Fields => 0,
      Fields           => (
            1 .. 0 => <>
      ),

      Properties => (
            1 .. 0 => <>
      )

   );
   

   Refinement_Decl_F_Pdu_For_Refinement_Decl : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Refinement_Decl_F_Pdu

         , Index => 1
   );
   Refinement_Decl_F_Field_For_Refinement_Decl : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Refinement_Decl_F_Field

         , Index => 2
   );
   Refinement_Decl_F_Sdu_For_Refinement_Decl : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Refinement_Decl_F_Sdu

         , Index => 3
   );
   Refinement_Decl_F_Condition_For_Refinement_Decl : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Refinement_Decl_F_Condition

         , Index => 4
   );

   Desc_For_Refinement_Decl : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 4,
      Properties_Count  => 0,

      Base_Type   => Common.Declaration_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("RefinementDecl"),

      Inherited_Fields => 0,
      Fields           => (
            1 => Refinement_Decl_F_Pdu_For_Refinement_Decl'Access, 2 => Refinement_Decl_F_Field_For_Refinement_Decl'Access, 3 => Refinement_Decl_F_Sdu_For_Refinement_Decl'Access, 4 => Refinement_Decl_F_Condition_For_Refinement_Decl'Access
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Refinement_Decl
   );
   

   Session_Decl_F_Parameters_For_Session_Decl : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Session_Decl_F_Parameters

         , Index => 1
   );
   Session_Decl_F_Identifier_For_Session_Decl : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Session_Decl_F_Identifier

         , Index => 2
   );
   Session_Decl_F_Declarations_For_Session_Decl : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Session_Decl_F_Declarations

         , Index => 3
   );
   Session_Decl_F_States_For_Session_Decl : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Session_Decl_F_States

         , Index => 4
   );
   Session_Decl_F_End_Identifier_For_Session_Decl : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Session_Decl_F_End_Identifier

         , Index => 5
   );

   Desc_For_Session_Decl : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 5,
      Properties_Count  => 0,

      Base_Type   => Common.Declaration_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("SessionDecl"),

      Inherited_Fields => 0,
      Fields           => (
            1 => Session_Decl_F_Parameters_For_Session_Decl'Access, 2 => Session_Decl_F_Identifier_For_Session_Decl'Access, 3 => Session_Decl_F_Declarations_For_Session_Decl'Access, 4 => Session_Decl_F_States_For_Session_Decl'Access, 5 => Session_Decl_F_End_Identifier_For_Session_Decl'Access
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Session_Decl
   );
   

   Type_Decl_F_Identifier_For_Type_Decl : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Type_Decl_F_Identifier

         , Index => 1
   );
   Type_Decl_F_Parameters_For_Type_Decl : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Type_Decl_F_Parameters

         , Index => 2
   );
   Type_Decl_F_Definition_For_Type_Decl : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Type_Decl_F_Definition

         , Index => 3
   );

   Desc_For_Type_Decl : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 3,
      Properties_Count  => 0,

      Base_Type   => Common.Declaration_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("TypeDecl"),

      Inherited_Fields => 0,
      Fields           => (
            1 => Type_Decl_F_Identifier_For_Type_Decl'Access, 2 => Type_Decl_F_Parameters_For_Type_Decl'Access, 3 => Type_Decl_F_Definition_For_Type_Decl'Access
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Type_Decl
   );
   

   Description_F_Content_For_Description : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Description_F_Content

         , Index => 1
   );

   Desc_For_Description : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 1,
      Properties_Count  => 0,

      Base_Type   => Common.R_F_L_X_Node_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("Description"),

      Inherited_Fields => 0,
      Fields           => (
            1 => Description_F_Content_For_Description'Access
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Description
   );
   

   Element_Value_Assoc_F_Identifier_For_Element_Value_Assoc : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Element_Value_Assoc_F_Identifier

         , Index => 1
   );
   Element_Value_Assoc_F_Literal_For_Element_Value_Assoc : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Element_Value_Assoc_F_Literal

         , Index => 2
   );

   Desc_For_Element_Value_Assoc : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 2,
      Properties_Count  => 0,

      Base_Type   => Common.R_F_L_X_Node_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("ElementValueAssoc"),

      Inherited_Fields => 0,
      Fields           => (
            1 => Element_Value_Assoc_F_Identifier_For_Element_Value_Assoc'Access, 2 => Element_Value_Assoc_F_Literal_For_Element_Value_Assoc'Access
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Element_Value_Assoc
   );
   


   Desc_For_Expr : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => True,
      Derivations_Count => 17,
      Fields_Count      => 0,
      Properties_Count  => 0,

      Base_Type   => Common.R_F_L_X_Node_Type_Id,
      Derivations =>
         (1 => Common.Attribute_Type_Id, 2 => Common.Bin_Op_Type_Id, 3 => Common.Binding_Type_Id, 4 => Common.Call_Type_Id, 5 => Common.Case_Expression_Type_Id, 6 => Common.Choice_Type_Id, 7 => Common.Comprehension_Type_Id, 8 => Common.Context_Item_Type_Id, 9 => Common.Conversion_Type_Id, 10 => Common.Message_Aggregate_Type_Id, 11 => Common.Negation_Type_Id, 12 => Common.Numeric_Literal_Type_Id, 13 => Common.Paren_Expression_Type_Id, 14 => Common.Quantified_Expression_Type_Id, 15 => Common.Select_Node_Type_Id, 16 => Common.Sequence_Literal_Type_Id, 17 => Common.Variable_Type_Id),

      DSL_Name => To_Unbounded_String ("Expr"),

      Inherited_Fields => 0,
      Fields           => (
            1 .. 0 => <>
      ),

      Properties => (
            1 .. 0 => <>
      )

   );
   

   Attribute_F_Expression_For_Attribute : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Attribute_F_Expression

         , Index => 1
   );
   Attribute_F_Kind_For_Attribute : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Attribute_F_Kind

         , Index => 2
   );

   Desc_For_Attribute : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 2,
      Properties_Count  => 0,

      Base_Type   => Common.Expr_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("Attribute"),

      Inherited_Fields => 0,
      Fields           => (
            1 => Attribute_F_Expression_For_Attribute'Access, 2 => Attribute_F_Kind_For_Attribute'Access
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Attribute
   );
   

   Bin_Op_F_Left_For_Bin_Op : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Bin_Op_F_Left

         , Index => 1
   );
   Bin_Op_F_Op_For_Bin_Op : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Bin_Op_F_Op

         , Index => 2
   );
   Bin_Op_F_Right_For_Bin_Op : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Bin_Op_F_Right

         , Index => 3
   );

   Desc_For_Bin_Op : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 3,
      Properties_Count  => 0,

      Base_Type   => Common.Expr_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("BinOp"),

      Inherited_Fields => 0,
      Fields           => (
            1 => Bin_Op_F_Left_For_Bin_Op'Access, 2 => Bin_Op_F_Op_For_Bin_Op'Access, 3 => Bin_Op_F_Right_For_Bin_Op'Access
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Bin_Op
   );
   

   Binding_F_Expression_For_Binding : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Binding_F_Expression

         , Index => 1
   );
   Binding_F_Bindings_For_Binding : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Binding_F_Bindings

         , Index => 2
   );

   Desc_For_Binding : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 2,
      Properties_Count  => 0,

      Base_Type   => Common.Expr_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("Binding"),

      Inherited_Fields => 0,
      Fields           => (
            1 => Binding_F_Expression_For_Binding'Access, 2 => Binding_F_Bindings_For_Binding'Access
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Binding
   );
   

   Call_F_Identifier_For_Call : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Call_F_Identifier

         , Index => 1
   );
   Call_F_Arguments_For_Call : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Call_F_Arguments

         , Index => 2
   );

   Desc_For_Call : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 2,
      Properties_Count  => 0,

      Base_Type   => Common.Expr_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("Call"),

      Inherited_Fields => 0,
      Fields           => (
            1 => Call_F_Identifier_For_Call'Access, 2 => Call_F_Arguments_For_Call'Access
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Call
   );
   

   Case_Expression_F_Expression_For_Case_Expression : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Case_Expression_F_Expression

         , Index => 1
   );
   Case_Expression_F_Choices_For_Case_Expression : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Case_Expression_F_Choices

         , Index => 2
   );

   Desc_For_Case_Expression : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 2,
      Properties_Count  => 0,

      Base_Type   => Common.Expr_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("CaseExpression"),

      Inherited_Fields => 0,
      Fields           => (
            1 => Case_Expression_F_Expression_For_Case_Expression'Access, 2 => Case_Expression_F_Choices_For_Case_Expression'Access
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Case_Expression
   );
   

   Choice_F_Selectors_For_Choice : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Choice_F_Selectors

         , Index => 1
   );
   Choice_F_Expression_For_Choice : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Choice_F_Expression

         , Index => 2
   );

   Desc_For_Choice : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 2,
      Properties_Count  => 0,

      Base_Type   => Common.Expr_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("Choice"),

      Inherited_Fields => 0,
      Fields           => (
            1 => Choice_F_Selectors_For_Choice'Access, 2 => Choice_F_Expression_For_Choice'Access
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Choice
   );
   

   Comprehension_F_Iterator_For_Comprehension : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Comprehension_F_Iterator

         , Index => 1
   );
   Comprehension_F_Sequence_For_Comprehension : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Comprehension_F_Sequence

         , Index => 2
   );
   Comprehension_F_Condition_For_Comprehension : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Comprehension_F_Condition

         , Index => 3
   );
   Comprehension_F_Selector_For_Comprehension : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Comprehension_F_Selector

         , Index => 4
   );

   Desc_For_Comprehension : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 4,
      Properties_Count  => 0,

      Base_Type   => Common.Expr_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("Comprehension"),

      Inherited_Fields => 0,
      Fields           => (
            1 => Comprehension_F_Iterator_For_Comprehension'Access, 2 => Comprehension_F_Sequence_For_Comprehension'Access, 3 => Comprehension_F_Condition_For_Comprehension'Access, 4 => Comprehension_F_Selector_For_Comprehension'Access
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Comprehension
   );
   

   Context_Item_F_Item_For_Context_Item : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Context_Item_F_Item

         , Index => 1
   );

   Desc_For_Context_Item : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 1,
      Properties_Count  => 0,

      Base_Type   => Common.Expr_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("ContextItem"),

      Inherited_Fields => 0,
      Fields           => (
            1 => Context_Item_F_Item_For_Context_Item'Access
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Context_Item
   );
   

   Conversion_F_Target_Identifier_For_Conversion : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Conversion_F_Target_Identifier

         , Index => 1
   );
   Conversion_F_Argument_For_Conversion : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Conversion_F_Argument

         , Index => 2
   );

   Desc_For_Conversion : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 2,
      Properties_Count  => 0,

      Base_Type   => Common.Expr_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("Conversion"),

      Inherited_Fields => 0,
      Fields           => (
            1 => Conversion_F_Target_Identifier_For_Conversion'Access, 2 => Conversion_F_Argument_For_Conversion'Access
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Conversion
   );
   

   Message_Aggregate_F_Identifier_For_Message_Aggregate : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Message_Aggregate_F_Identifier

         , Index => 1
   );
   Message_Aggregate_F_Values_For_Message_Aggregate : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Message_Aggregate_F_Values

         , Index => 2
   );

   Desc_For_Message_Aggregate : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 2,
      Properties_Count  => 0,

      Base_Type   => Common.Expr_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("MessageAggregate"),

      Inherited_Fields => 0,
      Fields           => (
            1 => Message_Aggregate_F_Identifier_For_Message_Aggregate'Access, 2 => Message_Aggregate_F_Values_For_Message_Aggregate'Access
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Message_Aggregate
   );
   

   Negation_F_Data_For_Negation : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Negation_F_Data

         , Index => 1
   );

   Desc_For_Negation : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 1,
      Properties_Count  => 0,

      Base_Type   => Common.Expr_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("Negation"),

      Inherited_Fields => 0,
      Fields           => (
            1 => Negation_F_Data_For_Negation'Access
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Negation
   );
   


   Desc_For_Numeric_Literal : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 0,
      Properties_Count  => 0,

      Base_Type   => Common.Expr_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("NumericLiteral"),

      Inherited_Fields => 0,
      Fields           => (
            1 .. 0 => <>
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Numeric_Literal
   );
   

   Paren_Expression_F_Data_For_Paren_Expression : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Paren_Expression_F_Data

         , Index => 1
   );

   Desc_For_Paren_Expression : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 1,
      Properties_Count  => 0,

      Base_Type   => Common.Expr_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("ParenExpression"),

      Inherited_Fields => 0,
      Fields           => (
            1 => Paren_Expression_F_Data_For_Paren_Expression'Access
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Paren_Expression
   );
   

   Quantified_Expression_F_Operation_For_Quantified_Expression : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Quantified_Expression_F_Operation

         , Index => 1
   );
   Quantified_Expression_F_Parameter_Identifier_For_Quantified_Expression : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Quantified_Expression_F_Parameter_Identifier

         , Index => 2
   );
   Quantified_Expression_F_Iterable_For_Quantified_Expression : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Quantified_Expression_F_Iterable

         , Index => 3
   );
   Quantified_Expression_F_Predicate_For_Quantified_Expression : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Quantified_Expression_F_Predicate

         , Index => 4
   );

   Desc_For_Quantified_Expression : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 4,
      Properties_Count  => 0,

      Base_Type   => Common.Expr_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("QuantifiedExpression"),

      Inherited_Fields => 0,
      Fields           => (
            1 => Quantified_Expression_F_Operation_For_Quantified_Expression'Access, 2 => Quantified_Expression_F_Parameter_Identifier_For_Quantified_Expression'Access, 3 => Quantified_Expression_F_Iterable_For_Quantified_Expression'Access, 4 => Quantified_Expression_F_Predicate_For_Quantified_Expression'Access
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Quantified_Expression
   );
   

   Select_Node_F_Expression_For_Select_Node : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Select_Node_F_Expression

         , Index => 1
   );
   Select_Node_F_Selector_For_Select_Node : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Select_Node_F_Selector

         , Index => 2
   );

   Desc_For_Select_Node : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 2,
      Properties_Count  => 0,

      Base_Type   => Common.Expr_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("Select"),

      Inherited_Fields => 0,
      Fields           => (
            1 => Select_Node_F_Expression_For_Select_Node'Access, 2 => Select_Node_F_Selector_For_Select_Node'Access
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Select_Node
   );
   


   Desc_For_Sequence_Literal : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => True,
      Derivations_Count => 3,
      Fields_Count      => 0,
      Properties_Count  => 0,

      Base_Type   => Common.Expr_Type_Id,
      Derivations =>
         (1 => Common.Concatenation_Type_Id, 2 => Common.Sequence_Aggregate_Type_Id, 3 => Common.String_Literal_Type_Id),

      DSL_Name => To_Unbounded_String ("SequenceLiteral"),

      Inherited_Fields => 0,
      Fields           => (
            1 .. 0 => <>
      ),

      Properties => (
            1 .. 0 => <>
      )

   );
   

   Concatenation_F_Left_For_Concatenation : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Concatenation_F_Left

         , Index => 1
   );
   Concatenation_F_Right_For_Concatenation : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Concatenation_F_Right

         , Index => 2
   );

   Desc_For_Concatenation : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 2,
      Properties_Count  => 0,

      Base_Type   => Common.Sequence_Literal_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("Concatenation"),

      Inherited_Fields => 0,
      Fields           => (
            1 => Concatenation_F_Left_For_Concatenation'Access, 2 => Concatenation_F_Right_For_Concatenation'Access
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Concatenation
   );
   

   Sequence_Aggregate_F_Values_For_Sequence_Aggregate : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Sequence_Aggregate_F_Values

         , Index => 1
   );

   Desc_For_Sequence_Aggregate : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 1,
      Properties_Count  => 0,

      Base_Type   => Common.Sequence_Literal_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("SequenceAggregate"),

      Inherited_Fields => 0,
      Fields           => (
            1 => Sequence_Aggregate_F_Values_For_Sequence_Aggregate'Access
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Sequence_Aggregate
   );
   


   Desc_For_String_Literal : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 0,
      Properties_Count  => 0,

      Base_Type   => Common.Sequence_Literal_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("StringLiteral"),

      Inherited_Fields => 0,
      Fields           => (
            1 .. 0 => <>
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_String_Literal
   );
   

   Variable_F_Identifier_For_Variable : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Variable_F_Identifier

         , Index => 1
   );

   Desc_For_Variable : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 1,
      Properties_Count  => 0,

      Base_Type   => Common.Expr_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("Variable"),

      Inherited_Fields => 0,
      Fields           => (
            1 => Variable_F_Identifier_For_Variable'Access
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Variable
   );
   


   Desc_For_Formal_Decl : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => True,
      Derivations_Count => 2,
      Fields_Count      => 0,
      Properties_Count  => 0,

      Base_Type   => Common.R_F_L_X_Node_Type_Id,
      Derivations =>
         (1 => Common.Formal_Channel_Decl_Type_Id, 2 => Common.Formal_Function_Decl_Type_Id),

      DSL_Name => To_Unbounded_String ("FormalDecl"),

      Inherited_Fields => 0,
      Fields           => (
            1 .. 0 => <>
      ),

      Properties => (
            1 .. 0 => <>
      )

   );
   

   Formal_Channel_Decl_F_Identifier_For_Formal_Channel_Decl : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Formal_Channel_Decl_F_Identifier

         , Index => 1
   );
   Formal_Channel_Decl_F_Parameters_For_Formal_Channel_Decl : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Formal_Channel_Decl_F_Parameters

         , Index => 2
   );

   Desc_For_Formal_Channel_Decl : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 2,
      Properties_Count  => 0,

      Base_Type   => Common.Formal_Decl_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("FormalChannelDecl"),

      Inherited_Fields => 0,
      Fields           => (
            1 => Formal_Channel_Decl_F_Identifier_For_Formal_Channel_Decl'Access, 2 => Formal_Channel_Decl_F_Parameters_For_Formal_Channel_Decl'Access
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Formal_Channel_Decl
   );
   

   Formal_Function_Decl_F_Identifier_For_Formal_Function_Decl : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Formal_Function_Decl_F_Identifier

         , Index => 1
   );
   Formal_Function_Decl_F_Parameters_For_Formal_Function_Decl : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Formal_Function_Decl_F_Parameters

         , Index => 2
   );
   Formal_Function_Decl_F_Return_Type_Identifier_For_Formal_Function_Decl : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Formal_Function_Decl_F_Return_Type_Identifier

         , Index => 3
   );

   Desc_For_Formal_Function_Decl : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 3,
      Properties_Count  => 0,

      Base_Type   => Common.Formal_Decl_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("FormalFunctionDecl"),

      Inherited_Fields => 0,
      Fields           => (
            1 => Formal_Function_Decl_F_Identifier_For_Formal_Function_Decl'Access, 2 => Formal_Function_Decl_F_Parameters_For_Formal_Function_Decl'Access, 3 => Formal_Function_Decl_F_Return_Type_Identifier_For_Formal_Function_Decl'Access
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Formal_Function_Decl
   );
   


   Desc_For_Local_Decl : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => True,
      Derivations_Count => 2,
      Fields_Count      => 0,
      Properties_Count  => 0,

      Base_Type   => Common.R_F_L_X_Node_Type_Id,
      Derivations =>
         (1 => Common.Renaming_Decl_Type_Id, 2 => Common.Variable_Decl_Type_Id),

      DSL_Name => To_Unbounded_String ("LocalDecl"),

      Inherited_Fields => 0,
      Fields           => (
            1 .. 0 => <>
      ),

      Properties => (
            1 .. 0 => <>
      )

   );
   

   Renaming_Decl_F_Identifier_For_Renaming_Decl : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Renaming_Decl_F_Identifier

         , Index => 1
   );
   Renaming_Decl_F_Type_Identifier_For_Renaming_Decl : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Renaming_Decl_F_Type_Identifier

         , Index => 2
   );
   Renaming_Decl_F_Expression_For_Renaming_Decl : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Renaming_Decl_F_Expression

         , Index => 3
   );

   Desc_For_Renaming_Decl : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 3,
      Properties_Count  => 0,

      Base_Type   => Common.Local_Decl_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("RenamingDecl"),

      Inherited_Fields => 0,
      Fields           => (
            1 => Renaming_Decl_F_Identifier_For_Renaming_Decl'Access, 2 => Renaming_Decl_F_Type_Identifier_For_Renaming_Decl'Access, 3 => Renaming_Decl_F_Expression_For_Renaming_Decl'Access
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Renaming_Decl
   );
   

   Variable_Decl_F_Identifier_For_Variable_Decl : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Variable_Decl_F_Identifier

         , Index => 1
   );
   Variable_Decl_F_Type_Identifier_For_Variable_Decl : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Variable_Decl_F_Type_Identifier

         , Index => 2
   );
   Variable_Decl_F_Initializer_For_Variable_Decl : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Variable_Decl_F_Initializer

         , Index => 3
   );

   Desc_For_Variable_Decl : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 3,
      Properties_Count  => 0,

      Base_Type   => Common.Local_Decl_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("VariableDecl"),

      Inherited_Fields => 0,
      Fields           => (
            1 => Variable_Decl_F_Identifier_For_Variable_Decl'Access, 2 => Variable_Decl_F_Type_Identifier_For_Variable_Decl'Access, 3 => Variable_Decl_F_Initializer_For_Variable_Decl'Access
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Variable_Decl
   );
   

   Message_Aggregate_Association_F_Identifier_For_Message_Aggregate_Association : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Message_Aggregate_Association_F_Identifier

         , Index => 1
   );
   Message_Aggregate_Association_F_Expression_For_Message_Aggregate_Association : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Message_Aggregate_Association_F_Expression

         , Index => 2
   );

   Desc_For_Message_Aggregate_Association : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 2,
      Properties_Count  => 0,

      Base_Type   => Common.R_F_L_X_Node_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("MessageAggregateAssociation"),

      Inherited_Fields => 0,
      Fields           => (
            1 => Message_Aggregate_Association_F_Identifier_For_Message_Aggregate_Association'Access, 2 => Message_Aggregate_Association_F_Expression_For_Message_Aggregate_Association'Access
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Message_Aggregate_Association
   );
   


   Desc_For_Message_Aspect : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => True,
      Derivations_Count => 2,
      Fields_Count      => 0,
      Properties_Count  => 0,

      Base_Type   => Common.R_F_L_X_Node_Type_Id,
      Derivations =>
         (1 => Common.Byte_Order_Aspect_Type_Id, 2 => Common.Checksum_Aspect_Type_Id),

      DSL_Name => To_Unbounded_String ("MessageAspect"),

      Inherited_Fields => 0,
      Fields           => (
            1 .. 0 => <>
      ),

      Properties => (
            1 .. 0 => <>
      )

   );
   

   Byte_Order_Aspect_F_Byte_Order_For_Byte_Order_Aspect : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Byte_Order_Aspect_F_Byte_Order

         , Index => 1
   );

   Desc_For_Byte_Order_Aspect : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 1,
      Properties_Count  => 0,

      Base_Type   => Common.Message_Aspect_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("ByteOrderAspect"),

      Inherited_Fields => 0,
      Fields           => (
            1 => Byte_Order_Aspect_F_Byte_Order_For_Byte_Order_Aspect'Access
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Byte_Order_Aspect
   );
   

   Checksum_Aspect_F_Associations_For_Checksum_Aspect : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Checksum_Aspect_F_Associations

         , Index => 1
   );

   Desc_For_Checksum_Aspect : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 1,
      Properties_Count  => 0,

      Base_Type   => Common.Message_Aspect_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("ChecksumAspect"),

      Inherited_Fields => 0,
      Fields           => (
            1 => Checksum_Aspect_F_Associations_For_Checksum_Aspect'Access
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Checksum_Aspect
   );
   

   Message_Field_F_Identifier_For_Message_Field : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Message_Field_F_Identifier

         , Index => 1
   );
   Message_Field_F_Type_Identifier_For_Message_Field : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Message_Field_F_Type_Identifier

         , Index => 2
   );
   Message_Field_F_Type_Arguments_For_Message_Field : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Message_Field_F_Type_Arguments

         , Index => 3
   );
   Message_Field_F_Aspects_For_Message_Field : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Message_Field_F_Aspects

         , Index => 4
   );
   Message_Field_F_Condition_For_Message_Field : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Message_Field_F_Condition

         , Index => 5
   );
   Message_Field_F_Thens_For_Message_Field : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Message_Field_F_Thens

         , Index => 6
   );

   Desc_For_Message_Field : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 6,
      Properties_Count  => 0,

      Base_Type   => Common.R_F_L_X_Node_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("MessageField"),

      Inherited_Fields => 0,
      Fields           => (
            1 => Message_Field_F_Identifier_For_Message_Field'Access, 2 => Message_Field_F_Type_Identifier_For_Message_Field'Access, 3 => Message_Field_F_Type_Arguments_For_Message_Field'Access, 4 => Message_Field_F_Aspects_For_Message_Field'Access, 5 => Message_Field_F_Condition_For_Message_Field'Access, 6 => Message_Field_F_Thens_For_Message_Field'Access
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Message_Field
   );
   

   Message_Fields_F_Initial_Field_For_Message_Fields : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Message_Fields_F_Initial_Field

         , Index => 1
   );
   Message_Fields_F_Fields_For_Message_Fields : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Message_Fields_F_Fields

         , Index => 2
   );

   Desc_For_Message_Fields : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 2,
      Properties_Count  => 0,

      Base_Type   => Common.R_F_L_X_Node_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("MessageFields"),

      Inherited_Fields => 0,
      Fields           => (
            1 => Message_Fields_F_Initial_Field_For_Message_Fields'Access, 2 => Message_Fields_F_Fields_For_Message_Fields'Access
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Message_Fields
   );
   

   Null_Message_Field_F_Then_For_Null_Message_Field : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Null_Message_Field_F_Then

         , Index => 1
   );

   Desc_For_Null_Message_Field : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 1,
      Properties_Count  => 0,

      Base_Type   => Common.R_F_L_X_Node_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("NullMessageField"),

      Inherited_Fields => 0,
      Fields           => (
            1 => Null_Message_Field_F_Then_For_Null_Message_Field'Access
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Null_Message_Field
   );
   


   Desc_For_Op : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => True,
      Derivations_Count => 16,
      Fields_Count      => 0,
      Properties_Count  => 0,

      Base_Type   => Common.R_F_L_X_Node_Type_Id,
      Derivations =>
         (1 => Common.Op_Add_Type_Id, 2 => Common.Op_And_Type_Id, 3 => Common.Op_Div_Type_Id, 4 => Common.Op_Eq_Type_Id, 5 => Common.Op_Ge_Type_Id, 6 => Common.Op_Gt_Type_Id, 7 => Common.Op_In_Type_Id, 8 => Common.Op_Le_Type_Id, 9 => Common.Op_Lt_Type_Id, 10 => Common.Op_Mod_Type_Id, 11 => Common.Op_Mul_Type_Id, 12 => Common.Op_Neq_Type_Id, 13 => Common.Op_Notin_Type_Id, 14 => Common.Op_Or_Type_Id, 15 => Common.Op_Pow_Type_Id, 16 => Common.Op_Sub_Type_Id),

      DSL_Name => To_Unbounded_String ("Op"),

      Inherited_Fields => 0,
      Fields           => (
            1 .. 0 => <>
      ),

      Properties => (
            1 .. 0 => <>
      )

   );
   


   Desc_For_Op_Add : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 0,
      Properties_Count  => 0,

      Base_Type   => Common.Op_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("Op.Add"),

      Inherited_Fields => 0,
      Fields           => (
            1 .. 0 => <>
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Op_Add
   );
   


   Desc_For_Op_And : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 0,
      Properties_Count  => 0,

      Base_Type   => Common.Op_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("Op.And"),

      Inherited_Fields => 0,
      Fields           => (
            1 .. 0 => <>
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Op_And
   );
   


   Desc_For_Op_Div : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 0,
      Properties_Count  => 0,

      Base_Type   => Common.Op_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("Op.Div"),

      Inherited_Fields => 0,
      Fields           => (
            1 .. 0 => <>
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Op_Div
   );
   


   Desc_For_Op_Eq : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 0,
      Properties_Count  => 0,

      Base_Type   => Common.Op_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("Op.Eq"),

      Inherited_Fields => 0,
      Fields           => (
            1 .. 0 => <>
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Op_Eq
   );
   


   Desc_For_Op_Ge : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 0,
      Properties_Count  => 0,

      Base_Type   => Common.Op_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("Op.Ge"),

      Inherited_Fields => 0,
      Fields           => (
            1 .. 0 => <>
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Op_Ge
   );
   


   Desc_For_Op_Gt : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 0,
      Properties_Count  => 0,

      Base_Type   => Common.Op_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("Op.Gt"),

      Inherited_Fields => 0,
      Fields           => (
            1 .. 0 => <>
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Op_Gt
   );
   


   Desc_For_Op_In : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 0,
      Properties_Count  => 0,

      Base_Type   => Common.Op_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("Op.In"),

      Inherited_Fields => 0,
      Fields           => (
            1 .. 0 => <>
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Op_In
   );
   


   Desc_For_Op_Le : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 0,
      Properties_Count  => 0,

      Base_Type   => Common.Op_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("Op.Le"),

      Inherited_Fields => 0,
      Fields           => (
            1 .. 0 => <>
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Op_Le
   );
   


   Desc_For_Op_Lt : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 0,
      Properties_Count  => 0,

      Base_Type   => Common.Op_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("Op.Lt"),

      Inherited_Fields => 0,
      Fields           => (
            1 .. 0 => <>
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Op_Lt
   );
   


   Desc_For_Op_Mod : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 0,
      Properties_Count  => 0,

      Base_Type   => Common.Op_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("Op.Mod"),

      Inherited_Fields => 0,
      Fields           => (
            1 .. 0 => <>
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Op_Mod
   );
   


   Desc_For_Op_Mul : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 0,
      Properties_Count  => 0,

      Base_Type   => Common.Op_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("Op.Mul"),

      Inherited_Fields => 0,
      Fields           => (
            1 .. 0 => <>
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Op_Mul
   );
   


   Desc_For_Op_Neq : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 0,
      Properties_Count  => 0,

      Base_Type   => Common.Op_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("Op.Neq"),

      Inherited_Fields => 0,
      Fields           => (
            1 .. 0 => <>
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Op_Neq
   );
   


   Desc_For_Op_Notin : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 0,
      Properties_Count  => 0,

      Base_Type   => Common.Op_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("Op.Notin"),

      Inherited_Fields => 0,
      Fields           => (
            1 .. 0 => <>
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Op_Notin
   );
   


   Desc_For_Op_Or : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 0,
      Properties_Count  => 0,

      Base_Type   => Common.Op_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("Op.Or"),

      Inherited_Fields => 0,
      Fields           => (
            1 .. 0 => <>
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Op_Or
   );
   


   Desc_For_Op_Pow : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 0,
      Properties_Count  => 0,

      Base_Type   => Common.Op_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("Op.Pow"),

      Inherited_Fields => 0,
      Fields           => (
            1 .. 0 => <>
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Op_Pow
   );
   


   Desc_For_Op_Sub : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 0,
      Properties_Count  => 0,

      Base_Type   => Common.Op_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("Op.Sub"),

      Inherited_Fields => 0,
      Fields           => (
            1 .. 0 => <>
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Op_Sub
   );
   

   Package_Node_F_Identifier_For_Package_Node : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Package_Node_F_Identifier

         , Index => 1
   );
   Package_Node_F_Declarations_For_Package_Node : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Package_Node_F_Declarations

         , Index => 2
   );
   Package_Node_F_End_Identifier_For_Package_Node : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Package_Node_F_End_Identifier

         , Index => 3
   );

   Desc_For_Package_Node : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 3,
      Properties_Count  => 0,

      Base_Type   => Common.R_F_L_X_Node_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("Package"),

      Inherited_Fields => 0,
      Fields           => (
            1 => Package_Node_F_Identifier_For_Package_Node'Access, 2 => Package_Node_F_Declarations_For_Package_Node'Access, 3 => Package_Node_F_End_Identifier_For_Package_Node'Access
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Package_Node
   );
   

   Parameter_F_Identifier_For_Parameter : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Parameter_F_Identifier

         , Index => 1
   );
   Parameter_F_Type_Identifier_For_Parameter : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Parameter_F_Type_Identifier

         , Index => 2
   );

   Desc_For_Parameter : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 2,
      Properties_Count  => 0,

      Base_Type   => Common.R_F_L_X_Node_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("Parameter"),

      Inherited_Fields => 0,
      Fields           => (
            1 => Parameter_F_Identifier_For_Parameter'Access, 2 => Parameter_F_Type_Identifier_For_Parameter'Access
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Parameter
   );
   

   Parameters_F_Parameters_For_Parameters : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Parameters_F_Parameters

         , Index => 1
   );

   Desc_For_Parameters : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 1,
      Properties_Count  => 0,

      Base_Type   => Common.R_F_L_X_Node_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("Parameters"),

      Inherited_Fields => 0,
      Fields           => (
            1 => Parameters_F_Parameters_For_Parameters'Access
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Parameters
   );
   


   Desc_For_Quantifier : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => True,
      Derivations_Count => 2,
      Fields_Count      => 0,
      Properties_Count  => 0,

      Base_Type   => Common.R_F_L_X_Node_Type_Id,
      Derivations =>
         (1 => Common.Quantifier_All_Type_Id, 2 => Common.Quantifier_Some_Type_Id),

      DSL_Name => To_Unbounded_String ("Quantifier"),

      Inherited_Fields => 0,
      Fields           => (
            1 .. 0 => <>
      ),

      Properties => (
            1 .. 0 => <>
      )

   );
   


   Desc_For_Quantifier_All : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 0,
      Properties_Count  => 0,

      Base_Type   => Common.Quantifier_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("Quantifier.All"),

      Inherited_Fields => 0,
      Fields           => (
            1 .. 0 => <>
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Quantifier_All
   );
   


   Desc_For_Quantifier_Some : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 0,
      Properties_Count  => 0,

      Base_Type   => Common.Quantifier_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("Quantifier.Some"),

      Inherited_Fields => 0,
      Fields           => (
            1 .. 0 => <>
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Quantifier_Some
   );
   


   Desc_For_R_F_L_X_Node_Base_List : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => True,
      Derivations_Count => 24,
      Fields_Count      => 0,
      Properties_Count  => 0,

      Base_Type   => Common.R_F_L_X_Node_Type_Id,
      Derivations =>
         (1 => Common.Aspect_List_Type_Id, 2 => Common.Base_Checksum_Val_List_Type_Id, 3 => Common.Channel_Attribute_List_Type_Id, 4 => Common.Checksum_Assoc_List_Type_Id, 5 => Common.Choice_List_Type_Id, 6 => Common.Conditional_Transition_List_Type_Id, 7 => Common.Context_Item_List_Type_Id, 8 => Common.Declaration_List_Type_Id, 9 => Common.Element_Value_Assoc_List_Type_Id, 10 => Common.Expr_List_Type_Id, 11 => Common.Formal_Decl_List_Type_Id, 12 => Common.Local_Decl_List_Type_Id, 13 => Common.Message_Aggregate_Association_List_Type_Id, 14 => Common.Message_Aspect_List_Type_Id, 15 => Common.Message_Field_List_Type_Id, 16 => Common.Numeric_Literal_List_Type_Id, 17 => Common.Parameter_List_Type_Id, 18 => Common.R_F_L_X_Node_List_Type_Id, 19 => Common.State_List_Type_Id, 20 => Common.Statement_List_Type_Id, 21 => Common.Term_Assoc_List_Type_Id, 22 => Common.Then_Node_List_Type_Id, 23 => Common.Type_Argument_List_Type_Id, 24 => Common.Unqualified_I_D_List_Type_Id),

      DSL_Name => To_Unbounded_String ("RFLXNodeBaseList"),

      Inherited_Fields => 0,
      Fields           => (
            1 .. 0 => <>
      ),

      Properties => (
            1 .. 0 => <>
      )

   );
   


   Desc_For_Aspect_List : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 0,
      Properties_Count  => 0,

      Base_Type   => Common.R_F_L_X_Node_Base_List_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("Aspect.list"),

      Inherited_Fields => 0,
      Fields           => (
            1 .. 0 => <>
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Aspect_List
   );
   


   Desc_For_Base_Checksum_Val_List : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 0,
      Properties_Count  => 0,

      Base_Type   => Common.R_F_L_X_Node_Base_List_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("BaseChecksumVal.list"),

      Inherited_Fields => 0,
      Fields           => (
            1 .. 0 => <>
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Base_Checksum_Val_List
   );
   


   Desc_For_Channel_Attribute_List : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 0,
      Properties_Count  => 0,

      Base_Type   => Common.R_F_L_X_Node_Base_List_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("ChannelAttribute.list"),

      Inherited_Fields => 0,
      Fields           => (
            1 .. 0 => <>
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Channel_Attribute_List
   );
   


   Desc_For_Checksum_Assoc_List : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 0,
      Properties_Count  => 0,

      Base_Type   => Common.R_F_L_X_Node_Base_List_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("ChecksumAssoc.list"),

      Inherited_Fields => 0,
      Fields           => (
            1 .. 0 => <>
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Checksum_Assoc_List
   );
   


   Desc_For_Choice_List : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 0,
      Properties_Count  => 0,

      Base_Type   => Common.R_F_L_X_Node_Base_List_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("Choice.list"),

      Inherited_Fields => 0,
      Fields           => (
            1 .. 0 => <>
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Choice_List
   );
   


   Desc_For_Conditional_Transition_List : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 0,
      Properties_Count  => 0,

      Base_Type   => Common.R_F_L_X_Node_Base_List_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("ConditionalTransition.list"),

      Inherited_Fields => 0,
      Fields           => (
            1 .. 0 => <>
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Conditional_Transition_List
   );
   


   Desc_For_Context_Item_List : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 0,
      Properties_Count  => 0,

      Base_Type   => Common.R_F_L_X_Node_Base_List_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("ContextItem.list"),

      Inherited_Fields => 0,
      Fields           => (
            1 .. 0 => <>
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Context_Item_List
   );
   


   Desc_For_Declaration_List : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 0,
      Properties_Count  => 0,

      Base_Type   => Common.R_F_L_X_Node_Base_List_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("Declaration.list"),

      Inherited_Fields => 0,
      Fields           => (
            1 .. 0 => <>
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Declaration_List
   );
   


   Desc_For_Element_Value_Assoc_List : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 0,
      Properties_Count  => 0,

      Base_Type   => Common.R_F_L_X_Node_Base_List_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("ElementValueAssoc.list"),

      Inherited_Fields => 0,
      Fields           => (
            1 .. 0 => <>
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Element_Value_Assoc_List
   );
   


   Desc_For_Expr_List : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 0,
      Properties_Count  => 0,

      Base_Type   => Common.R_F_L_X_Node_Base_List_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("Expr.list"),

      Inherited_Fields => 0,
      Fields           => (
            1 .. 0 => <>
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Expr_List
   );
   


   Desc_For_Formal_Decl_List : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 0,
      Properties_Count  => 0,

      Base_Type   => Common.R_F_L_X_Node_Base_List_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("FormalDecl.list"),

      Inherited_Fields => 0,
      Fields           => (
            1 .. 0 => <>
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Formal_Decl_List
   );
   


   Desc_For_Local_Decl_List : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 0,
      Properties_Count  => 0,

      Base_Type   => Common.R_F_L_X_Node_Base_List_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("LocalDecl.list"),

      Inherited_Fields => 0,
      Fields           => (
            1 .. 0 => <>
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Local_Decl_List
   );
   


   Desc_For_Message_Aggregate_Association_List : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 0,
      Properties_Count  => 0,

      Base_Type   => Common.R_F_L_X_Node_Base_List_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("MessageAggregateAssociation.list"),

      Inherited_Fields => 0,
      Fields           => (
            1 .. 0 => <>
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Message_Aggregate_Association_List
   );
   


   Desc_For_Message_Aspect_List : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 0,
      Properties_Count  => 0,

      Base_Type   => Common.R_F_L_X_Node_Base_List_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("MessageAspect.list"),

      Inherited_Fields => 0,
      Fields           => (
            1 .. 0 => <>
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Message_Aspect_List
   );
   


   Desc_For_Message_Field_List : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 0,
      Properties_Count  => 0,

      Base_Type   => Common.R_F_L_X_Node_Base_List_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("MessageField.list"),

      Inherited_Fields => 0,
      Fields           => (
            1 .. 0 => <>
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Message_Field_List
   );
   


   Desc_For_Numeric_Literal_List : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 0,
      Properties_Count  => 0,

      Base_Type   => Common.R_F_L_X_Node_Base_List_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("NumericLiteral.list"),

      Inherited_Fields => 0,
      Fields           => (
            1 .. 0 => <>
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Numeric_Literal_List
   );
   


   Desc_For_Parameter_List : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 0,
      Properties_Count  => 0,

      Base_Type   => Common.R_F_L_X_Node_Base_List_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("Parameter.list"),

      Inherited_Fields => 0,
      Fields           => (
            1 .. 0 => <>
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Parameter_List
   );
   


   Desc_For_R_F_L_X_Node_List : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 0,
      Properties_Count  => 0,

      Base_Type   => Common.R_F_L_X_Node_Base_List_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("RFLXNode.list"),

      Inherited_Fields => 0,
      Fields           => (
            1 .. 0 => <>
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_R_F_L_X_Node_List
   );
   


   Desc_For_State_List : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 0,
      Properties_Count  => 0,

      Base_Type   => Common.R_F_L_X_Node_Base_List_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("State.list"),

      Inherited_Fields => 0,
      Fields           => (
            1 .. 0 => <>
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_State_List
   );
   


   Desc_For_Statement_List : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 0,
      Properties_Count  => 0,

      Base_Type   => Common.R_F_L_X_Node_Base_List_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("Statement.list"),

      Inherited_Fields => 0,
      Fields           => (
            1 .. 0 => <>
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Statement_List
   );
   


   Desc_For_Term_Assoc_List : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 0,
      Properties_Count  => 0,

      Base_Type   => Common.R_F_L_X_Node_Base_List_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("TermAssoc.list"),

      Inherited_Fields => 0,
      Fields           => (
            1 .. 0 => <>
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Term_Assoc_List
   );
   


   Desc_For_Then_Node_List : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 0,
      Properties_Count  => 0,

      Base_Type   => Common.R_F_L_X_Node_Base_List_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("Then.list"),

      Inherited_Fields => 0,
      Fields           => (
            1 .. 0 => <>
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Then_Node_List
   );
   


   Desc_For_Type_Argument_List : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 0,
      Properties_Count  => 0,

      Base_Type   => Common.R_F_L_X_Node_Base_List_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("TypeArgument.list"),

      Inherited_Fields => 0,
      Fields           => (
            1 .. 0 => <>
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Type_Argument_List
   );
   


   Desc_For_Unqualified_I_D_List : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 0,
      Properties_Count  => 0,

      Base_Type   => Common.R_F_L_X_Node_Base_List_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("UnqualifiedID.list"),

      Inherited_Fields => 0,
      Fields           => (
            1 .. 0 => <>
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Unqualified_I_D_List
   );
   

   Specification_F_Context_Clause_For_Specification : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Specification_F_Context_Clause

         , Index => 1
   );
   Specification_F_Package_Declaration_For_Specification : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Specification_F_Package_Declaration

         , Index => 2
   );

   Desc_For_Specification : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 2,
      Properties_Count  => 0,

      Base_Type   => Common.R_F_L_X_Node_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("Specification"),

      Inherited_Fields => 0,
      Fields           => (
            1 => Specification_F_Context_Clause_For_Specification'Access, 2 => Specification_F_Package_Declaration_For_Specification'Access
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Specification
   );
   

   State_F_Identifier_For_State : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => State_F_Identifier

         , Index => 1
   );
   State_F_Description_For_State : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => State_F_Description

         , Index => 2
   );
   State_F_Body_For_State : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => State_F_Body

         , Index => 3
   );

   Desc_For_State : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 3,
      Properties_Count  => 0,

      Base_Type   => Common.R_F_L_X_Node_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("State"),

      Inherited_Fields => 0,
      Fields           => (
            1 => State_F_Identifier_For_State'Access, 2 => State_F_Description_For_State'Access, 3 => State_F_Body_For_State'Access
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_State
   );
   

   State_Body_F_Declarations_For_State_Body : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => State_Body_F_Declarations

         , Index => 1
   );
   State_Body_F_Actions_For_State_Body : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => State_Body_F_Actions

         , Index => 2
   );
   State_Body_F_Conditional_Transitions_For_State_Body : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => State_Body_F_Conditional_Transitions

         , Index => 3
   );
   State_Body_F_Final_Transition_For_State_Body : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => State_Body_F_Final_Transition

         , Index => 4
   );
   State_Body_F_Exception_Transition_For_State_Body : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => State_Body_F_Exception_Transition

         , Index => 5
   );
   State_Body_F_End_Identifier_For_State_Body : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => State_Body_F_End_Identifier

         , Index => 6
   );

   Desc_For_State_Body : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 6,
      Properties_Count  => 0,

      Base_Type   => Common.R_F_L_X_Node_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("StateBody"),

      Inherited_Fields => 0,
      Fields           => (
            1 => State_Body_F_Declarations_For_State_Body'Access, 2 => State_Body_F_Actions_For_State_Body'Access, 3 => State_Body_F_Conditional_Transitions_For_State_Body'Access, 4 => State_Body_F_Final_Transition_For_State_Body'Access, 5 => State_Body_F_Exception_Transition_For_State_Body'Access, 6 => State_Body_F_End_Identifier_For_State_Body'Access
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_State_Body
   );
   


   Desc_For_Statement : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => True,
      Derivations_Count => 4,
      Fields_Count      => 0,
      Properties_Count  => 0,

      Base_Type   => Common.R_F_L_X_Node_Type_Id,
      Derivations =>
         (1 => Common.Assignment_Type_Id, 2 => Common.Attribute_Statement_Type_Id, 3 => Common.Message_Field_Assignment_Type_Id, 4 => Common.Reset_Type_Id),

      DSL_Name => To_Unbounded_String ("Statement"),

      Inherited_Fields => 0,
      Fields           => (
            1 .. 0 => <>
      ),

      Properties => (
            1 .. 0 => <>
      )

   );
   

   Assignment_F_Identifier_For_Assignment : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Assignment_F_Identifier

         , Index => 1
   );
   Assignment_F_Expression_For_Assignment : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Assignment_F_Expression

         , Index => 2
   );

   Desc_For_Assignment : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 2,
      Properties_Count  => 0,

      Base_Type   => Common.Statement_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("Assignment"),

      Inherited_Fields => 0,
      Fields           => (
            1 => Assignment_F_Identifier_For_Assignment'Access, 2 => Assignment_F_Expression_For_Assignment'Access
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Assignment
   );
   

   Attribute_Statement_F_Identifier_For_Attribute_Statement : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Attribute_Statement_F_Identifier

         , Index => 1
   );
   Attribute_Statement_F_Attr_For_Attribute_Statement : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Attribute_Statement_F_Attr

         , Index => 2
   );
   Attribute_Statement_F_Expression_For_Attribute_Statement : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Attribute_Statement_F_Expression

         , Index => 3
   );

   Desc_For_Attribute_Statement : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 3,
      Properties_Count  => 0,

      Base_Type   => Common.Statement_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("AttributeStatement"),

      Inherited_Fields => 0,
      Fields           => (
            1 => Attribute_Statement_F_Identifier_For_Attribute_Statement'Access, 2 => Attribute_Statement_F_Attr_For_Attribute_Statement'Access, 3 => Attribute_Statement_F_Expression_For_Attribute_Statement'Access
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Attribute_Statement
   );
   

   Message_Field_Assignment_F_Message_For_Message_Field_Assignment : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Message_Field_Assignment_F_Message

         , Index => 1
   );
   Message_Field_Assignment_F_Field_For_Message_Field_Assignment : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Message_Field_Assignment_F_Field

         , Index => 2
   );
   Message_Field_Assignment_F_Expression_For_Message_Field_Assignment : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Message_Field_Assignment_F_Expression

         , Index => 3
   );

   Desc_For_Message_Field_Assignment : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 3,
      Properties_Count  => 0,

      Base_Type   => Common.Statement_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("MessageFieldAssignment"),

      Inherited_Fields => 0,
      Fields           => (
            1 => Message_Field_Assignment_F_Message_For_Message_Field_Assignment'Access, 2 => Message_Field_Assignment_F_Field_For_Message_Field_Assignment'Access, 3 => Message_Field_Assignment_F_Expression_For_Message_Field_Assignment'Access
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Message_Field_Assignment
   );
   

   Reset_F_Identifier_For_Reset : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Reset_F_Identifier

         , Index => 1
   );
   Reset_F_Associations_For_Reset : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Reset_F_Associations

         , Index => 2
   );

   Desc_For_Reset : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 2,
      Properties_Count  => 0,

      Base_Type   => Common.Statement_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("Reset"),

      Inherited_Fields => 0,
      Fields           => (
            1 => Reset_F_Identifier_For_Reset'Access, 2 => Reset_F_Associations_For_Reset'Access
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Reset
   );
   

   Term_Assoc_F_Identifier_For_Term_Assoc : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Term_Assoc_F_Identifier

         , Index => 1
   );
   Term_Assoc_F_Expression_For_Term_Assoc : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Term_Assoc_F_Expression

         , Index => 2
   );

   Desc_For_Term_Assoc : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 2,
      Properties_Count  => 0,

      Base_Type   => Common.R_F_L_X_Node_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("TermAssoc"),

      Inherited_Fields => 0,
      Fields           => (
            1 => Term_Assoc_F_Identifier_For_Term_Assoc'Access, 2 => Term_Assoc_F_Expression_For_Term_Assoc'Access
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Term_Assoc
   );
   

   Then_Node_F_Target_For_Then_Node : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Then_Node_F_Target

         , Index => 1
   );
   Then_Node_F_Aspects_For_Then_Node : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Then_Node_F_Aspects

         , Index => 2
   );
   Then_Node_F_Condition_For_Then_Node : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Then_Node_F_Condition

         , Index => 3
   );

   Desc_For_Then_Node : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 3,
      Properties_Count  => 0,

      Base_Type   => Common.R_F_L_X_Node_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("Then"),

      Inherited_Fields => 0,
      Fields           => (
            1 => Then_Node_F_Target_For_Then_Node'Access, 2 => Then_Node_F_Aspects_For_Then_Node'Access, 3 => Then_Node_F_Condition_For_Then_Node'Access
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Then_Node
   );
   

   Transition_F_Target_For_Transition : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Transition_F_Target

         , Index => 1
   );
   Transition_F_Description_For_Transition : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Transition_F_Description

         , Index => 2
   );

   Desc_For_Transition : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 1,
      Fields_Count      => 2,
      Properties_Count  => 0,

      Base_Type   => Common.R_F_L_X_Node_Type_Id,
      Derivations =>
         (1 => Common.Conditional_Transition_Type_Id),

      DSL_Name => To_Unbounded_String ("Transition"),

      Inherited_Fields => 0,
      Fields           => (
            1 => Transition_F_Target_For_Transition'Access, 2 => Transition_F_Description_For_Transition'Access
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Transition
   );
   

   Conditional_Transition_F_Condition_For_Conditional_Transition : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Conditional_Transition_F_Condition

         , Index => 3
   );

   Desc_For_Conditional_Transition : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 1,
      Properties_Count  => 0,

      Base_Type   => Common.Transition_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("ConditionalTransition"),

      Inherited_Fields => 2,
      Fields           => (
            1 => Conditional_Transition_F_Condition_For_Conditional_Transition'Access
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Conditional_Transition
   );
   

   Type_Argument_F_Identifier_For_Type_Argument : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Type_Argument_F_Identifier

         , Index => 1
   );
   Type_Argument_F_Expression_For_Type_Argument : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Type_Argument_F_Expression

         , Index => 2
   );

   Desc_For_Type_Argument : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 2,
      Properties_Count  => 0,

      Base_Type   => Common.R_F_L_X_Node_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("TypeArgument"),

      Inherited_Fields => 0,
      Fields           => (
            1 => Type_Argument_F_Identifier_For_Type_Argument'Access, 2 => Type_Argument_F_Expression_For_Type_Argument'Access
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Type_Argument
   );
   


   Desc_For_Type_Def : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => True,
      Derivations_Count => 6,
      Fields_Count      => 0,
      Properties_Count  => 0,

      Base_Type   => Common.R_F_L_X_Node_Type_Id,
      Derivations =>
         (1 => Common.Abstract_Message_Type_Def_Type_Id, 2 => Common.Enumeration_Def_Type_Id, 3 => Common.Enumeration_Type_Def_Type_Id, 4 => Common.Integer_Type_Def_Type_Id, 5 => Common.Sequence_Type_Def_Type_Id, 6 => Common.Type_Derivation_Def_Type_Id),

      DSL_Name => To_Unbounded_String ("TypeDef"),

      Inherited_Fields => 0,
      Fields           => (
            1 .. 0 => <>
      ),

      Properties => (
            1 .. 0 => <>
      )

   );
   


   Desc_For_Abstract_Message_Type_Def : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => True,
      Derivations_Count => 2,
      Fields_Count      => 0,
      Properties_Count  => 0,

      Base_Type   => Common.Type_Def_Type_Id,
      Derivations =>
         (1 => Common.Message_Type_Def_Type_Id, 2 => Common.Null_Message_Type_Def_Type_Id),

      DSL_Name => To_Unbounded_String ("AbstractMessageTypeDef"),

      Inherited_Fields => 0,
      Fields           => (
            1 .. 0 => <>
      ),

      Properties => (
            1 .. 0 => <>
      )

   );
   

   Message_Type_Def_F_Message_Fields_For_Message_Type_Def : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Message_Type_Def_F_Message_Fields

         , Index => 1
   );
   Message_Type_Def_F_Aspects_For_Message_Type_Def : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Message_Type_Def_F_Aspects

         , Index => 2
   );

   Desc_For_Message_Type_Def : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 2,
      Properties_Count  => 0,

      Base_Type   => Common.Abstract_Message_Type_Def_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("MessageTypeDef"),

      Inherited_Fields => 0,
      Fields           => (
            1 => Message_Type_Def_F_Message_Fields_For_Message_Type_Def'Access, 2 => Message_Type_Def_F_Aspects_For_Message_Type_Def'Access
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Message_Type_Def
   );
   


   Desc_For_Null_Message_Type_Def : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 0,
      Properties_Count  => 0,

      Base_Type   => Common.Abstract_Message_Type_Def_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("NullMessageTypeDef"),

      Inherited_Fields => 0,
      Fields           => (
            1 .. 0 => <>
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Null_Message_Type_Def
   );
   


   Desc_For_Enumeration_Def : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => True,
      Derivations_Count => 2,
      Fields_Count      => 0,
      Properties_Count  => 0,

      Base_Type   => Common.Type_Def_Type_Id,
      Derivations =>
         (1 => Common.Named_Enumeration_Def_Type_Id, 2 => Common.Positional_Enumeration_Def_Type_Id),

      DSL_Name => To_Unbounded_String ("EnumerationDef"),

      Inherited_Fields => 0,
      Fields           => (
            1 .. 0 => <>
      ),

      Properties => (
            1 .. 0 => <>
      )

   );
   

   Named_Enumeration_Def_F_Elements_For_Named_Enumeration_Def : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Named_Enumeration_Def_F_Elements

         , Index => 1
   );

   Desc_For_Named_Enumeration_Def : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 1,
      Properties_Count  => 0,

      Base_Type   => Common.Enumeration_Def_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("NamedEnumerationDef"),

      Inherited_Fields => 0,
      Fields           => (
            1 => Named_Enumeration_Def_F_Elements_For_Named_Enumeration_Def'Access
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Named_Enumeration_Def
   );
   

   Positional_Enumeration_Def_F_Elements_For_Positional_Enumeration_Def : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Positional_Enumeration_Def_F_Elements

         , Index => 1
   );

   Desc_For_Positional_Enumeration_Def : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 1,
      Properties_Count  => 0,

      Base_Type   => Common.Enumeration_Def_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("PositionalEnumerationDef"),

      Inherited_Fields => 0,
      Fields           => (
            1 => Positional_Enumeration_Def_F_Elements_For_Positional_Enumeration_Def'Access
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Positional_Enumeration_Def
   );
   

   Enumeration_Type_Def_F_Elements_For_Enumeration_Type_Def : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Enumeration_Type_Def_F_Elements

         , Index => 1
   );
   Enumeration_Type_Def_F_Aspects_For_Enumeration_Type_Def : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Enumeration_Type_Def_F_Aspects

         , Index => 2
   );

   Desc_For_Enumeration_Type_Def : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 2,
      Properties_Count  => 0,

      Base_Type   => Common.Type_Def_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("EnumerationTypeDef"),

      Inherited_Fields => 0,
      Fields           => (
            1 => Enumeration_Type_Def_F_Elements_For_Enumeration_Type_Def'Access, 2 => Enumeration_Type_Def_F_Aspects_For_Enumeration_Type_Def'Access
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Enumeration_Type_Def
   );
   


   Desc_For_Integer_Type_Def : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => True,
      Derivations_Count => 2,
      Fields_Count      => 0,
      Properties_Count  => 0,

      Base_Type   => Common.Type_Def_Type_Id,
      Derivations =>
         (1 => Common.Modular_Type_Def_Type_Id, 2 => Common.Range_Type_Def_Type_Id),

      DSL_Name => To_Unbounded_String ("IntegerTypeDef"),

      Inherited_Fields => 0,
      Fields           => (
            1 .. 0 => <>
      ),

      Properties => (
            1 .. 0 => <>
      )

   );
   

   Modular_Type_Def_F_Mod_For_Modular_Type_Def : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Modular_Type_Def_F_Mod

         , Index => 1
   );

   Desc_For_Modular_Type_Def : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 1,
      Properties_Count  => 0,

      Base_Type   => Common.Integer_Type_Def_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("ModularTypeDef"),

      Inherited_Fields => 0,
      Fields           => (
            1 => Modular_Type_Def_F_Mod_For_Modular_Type_Def'Access
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Modular_Type_Def
   );
   

   Range_Type_Def_F_First_For_Range_Type_Def : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Range_Type_Def_F_First

         , Index => 1
   );
   Range_Type_Def_F_Last_For_Range_Type_Def : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Range_Type_Def_F_Last

         , Index => 2
   );
   Range_Type_Def_F_Size_For_Range_Type_Def : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Range_Type_Def_F_Size

         , Index => 3
   );

   Desc_For_Range_Type_Def : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 3,
      Properties_Count  => 0,

      Base_Type   => Common.Integer_Type_Def_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("RangeTypeDef"),

      Inherited_Fields => 0,
      Fields           => (
            1 => Range_Type_Def_F_First_For_Range_Type_Def'Access, 2 => Range_Type_Def_F_Last_For_Range_Type_Def'Access, 3 => Range_Type_Def_F_Size_For_Range_Type_Def'Access
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Range_Type_Def
   );
   

   Sequence_Type_Def_F_Element_Type_For_Sequence_Type_Def : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Sequence_Type_Def_F_Element_Type

         , Index => 1
   );

   Desc_For_Sequence_Type_Def : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 1,
      Properties_Count  => 0,

      Base_Type   => Common.Type_Def_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("SequenceTypeDef"),

      Inherited_Fields => 0,
      Fields           => (
            1 => Sequence_Type_Def_F_Element_Type_For_Sequence_Type_Def'Access
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Sequence_Type_Def
   );
   

   Type_Derivation_Def_F_Base_For_Type_Derivation_Def : aliased constant Node_Field_Descriptor
   := (
      Is_Abstract_Or_Null => False,
      Field               => Type_Derivation_Def_F_Base

         , Index => 1
   );

   Desc_For_Type_Derivation_Def : aliased constant Node_Type_Descriptor := (
      Is_Abstract       => False,
      Derivations_Count => 0,
      Fields_Count      => 1,
      Properties_Count  => 0,

      Base_Type   => Common.Type_Def_Type_Id,
      Derivations =>
         (1 .. 0 => <>),

      DSL_Name => To_Unbounded_String ("TypeDerivationDef"),

      Inherited_Fields => 0,
      Fields           => (
            1 => Type_Derivation_Def_F_Base_For_Type_Derivation_Def'Access
      ),

      Properties => (
            1 .. 0 => <>
      )

      , Kind => Rflx_Type_Derivation_Def
   );

   Node_Type_Descriptors : constant
      array (Node_Type_Id) of Node_Type_Descriptor_Access
   := (Desc_For_R_F_L_X_Node'Access, Desc_For_Abstract_I_D'Access, Desc_For_I_D'Access, Desc_For_Unqualified_I_D'Access, Desc_For_Aspect'Access, Desc_For_Attr'Access, Desc_For_Attr_First'Access, Desc_For_Attr_Has_Data'Access, Desc_For_Attr_Head'Access, Desc_For_Attr_Last'Access, Desc_For_Attr_Opaque'Access, Desc_For_Attr_Present'Access, Desc_For_Attr_Size'Access, Desc_For_Attr_Valid'Access, Desc_For_Attr_Valid_Checksum'Access, Desc_For_Attr_Stmt'Access, Desc_For_Attr_Stmt_Append'Access, Desc_For_Attr_Stmt_Extend'Access, Desc_For_Attr_Stmt_Read'Access, Desc_For_Attr_Stmt_Write'Access, Desc_For_Base_Aggregate'Access, Desc_For_Message_Aggregate_Associations'Access, Desc_For_Null_Message_Aggregate'Access, Desc_For_Base_Checksum_Val'Access, Desc_For_Checksum_Val'Access, Desc_For_Checksum_Value_Range'Access, Desc_For_Byte_Order_Type'Access, Desc_For_Byte_Order_Type_Highorderfirst'Access, Desc_For_Byte_Order_Type_Loworderfirst'Access, Desc_For_Channel_Attribute'Access, Desc_For_Readable'Access, Desc_For_Writable'Access, Desc_For_Checksum_Assoc'Access, Desc_For_Declaration'Access, Desc_For_Refinement_Decl'Access, Desc_For_Session_Decl'Access, Desc_For_Type_Decl'Access, Desc_For_Description'Access, Desc_For_Element_Value_Assoc'Access, Desc_For_Expr'Access, Desc_For_Attribute'Access, Desc_For_Bin_Op'Access, Desc_For_Binding'Access, Desc_For_Call'Access, Desc_For_Case_Expression'Access, Desc_For_Choice'Access, Desc_For_Comprehension'Access, Desc_For_Context_Item'Access, Desc_For_Conversion'Access, Desc_For_Message_Aggregate'Access, Desc_For_Negation'Access, Desc_For_Numeric_Literal'Access, Desc_For_Paren_Expression'Access, Desc_For_Quantified_Expression'Access, Desc_For_Select_Node'Access, Desc_For_Sequence_Literal'Access, Desc_For_Concatenation'Access, Desc_For_Sequence_Aggregate'Access, Desc_For_String_Literal'Access, Desc_For_Variable'Access, Desc_For_Formal_Decl'Access, Desc_For_Formal_Channel_Decl'Access, Desc_For_Formal_Function_Decl'Access, Desc_For_Local_Decl'Access, Desc_For_Renaming_Decl'Access, Desc_For_Variable_Decl'Access, Desc_For_Message_Aggregate_Association'Access, Desc_For_Message_Aspect'Access, Desc_For_Byte_Order_Aspect'Access, Desc_For_Checksum_Aspect'Access, Desc_For_Message_Field'Access, Desc_For_Message_Fields'Access, Desc_For_Null_Message_Field'Access, Desc_For_Op'Access, Desc_For_Op_Add'Access, Desc_For_Op_And'Access, Desc_For_Op_Div'Access, Desc_For_Op_Eq'Access, Desc_For_Op_Ge'Access, Desc_For_Op_Gt'Access, Desc_For_Op_In'Access, Desc_For_Op_Le'Access, Desc_For_Op_Lt'Access, Desc_For_Op_Mod'Access, Desc_For_Op_Mul'Access, Desc_For_Op_Neq'Access, Desc_For_Op_Notin'Access, Desc_For_Op_Or'Access, Desc_For_Op_Pow'Access, Desc_For_Op_Sub'Access, Desc_For_Package_Node'Access, Desc_For_Parameter'Access, Desc_For_Parameters'Access, Desc_For_Quantifier'Access, Desc_For_Quantifier_All'Access, Desc_For_Quantifier_Some'Access, Desc_For_R_F_L_X_Node_Base_List'Access, Desc_For_Aspect_List'Access, Desc_For_Base_Checksum_Val_List'Access, Desc_For_Channel_Attribute_List'Access, Desc_For_Checksum_Assoc_List'Access, Desc_For_Choice_List'Access, Desc_For_Conditional_Transition_List'Access, Desc_For_Context_Item_List'Access, Desc_For_Declaration_List'Access, Desc_For_Element_Value_Assoc_List'Access, Desc_For_Expr_List'Access, Desc_For_Formal_Decl_List'Access, Desc_For_Local_Decl_List'Access, Desc_For_Message_Aggregate_Association_List'Access, Desc_For_Message_Aspect_List'Access, Desc_For_Message_Field_List'Access, Desc_For_Numeric_Literal_List'Access, Desc_For_Parameter_List'Access, Desc_For_R_F_L_X_Node_List'Access, Desc_For_State_List'Access, Desc_For_Statement_List'Access, Desc_For_Term_Assoc_List'Access, Desc_For_Then_Node_List'Access, Desc_For_Type_Argument_List'Access, Desc_For_Unqualified_I_D_List'Access, Desc_For_Specification'Access, Desc_For_State'Access, Desc_For_State_Body'Access, Desc_For_Statement'Access, Desc_For_Assignment'Access, Desc_For_Attribute_Statement'Access, Desc_For_Message_Field_Assignment'Access, Desc_For_Reset'Access, Desc_For_Term_Assoc'Access, Desc_For_Then_Node'Access, Desc_For_Transition'Access, Desc_For_Conditional_Transition'Access, Desc_For_Type_Argument'Access, Desc_For_Type_Def'Access, Desc_For_Abstract_Message_Type_Def'Access, Desc_For_Message_Type_Def'Access, Desc_For_Null_Message_Type_Def'Access, Desc_For_Enumeration_Def'Access, Desc_For_Named_Enumeration_Def'Access, Desc_For_Positional_Enumeration_Def'Access, Desc_For_Enumeration_Type_Def'Access, Desc_For_Integer_Type_Def'Access, Desc_For_Modular_Type_Def'Access, Desc_For_Range_Type_Def'Access, Desc_For_Sequence_Type_Def'Access, Desc_For_Type_Derivation_Def'Access);

   ----------------------
   -- Various mappings --
   ----------------------

   package Node_Type_Id_Maps is new Ada.Containers.Hashed_Maps
     (Key_Type        => Unbounded_String,
      Element_Type    => Node_Type_Id,
      Equivalent_Keys => "=",
      Hash            => Hash);

   DSL_Name_To_Node_Type : Node_Type_Id_Maps.Map;
   --  Lookup table for DSL names to node type references. Created at
   --  elaboration time and never updated after.

   Kind_To_Id : constant array (R_F_L_X_Node_Kind_Type) of Node_Type_Id := (
      Rflx_I_D => Common.I_D_Type_Id, Rflx_Unqualified_I_D => Common.Unqualified_I_D_Type_Id, Rflx_Aspect => Common.Aspect_Type_Id, Rflx_Attr_First => Common.Attr_First_Type_Id, Rflx_Attr_Has_Data => Common.Attr_Has_Data_Type_Id, Rflx_Attr_Head => Common.Attr_Head_Type_Id, Rflx_Attr_Last => Common.Attr_Last_Type_Id, Rflx_Attr_Opaque => Common.Attr_Opaque_Type_Id, Rflx_Attr_Present => Common.Attr_Present_Type_Id, Rflx_Attr_Size => Common.Attr_Size_Type_Id, Rflx_Attr_Valid => Common.Attr_Valid_Type_Id, Rflx_Attr_Valid_Checksum => Common.Attr_Valid_Checksum_Type_Id, Rflx_Attr_Stmt_Append => Common.Attr_Stmt_Append_Type_Id, Rflx_Attr_Stmt_Extend => Common.Attr_Stmt_Extend_Type_Id, Rflx_Attr_Stmt_Read => Common.Attr_Stmt_Read_Type_Id, Rflx_Attr_Stmt_Write => Common.Attr_Stmt_Write_Type_Id, Rflx_Message_Aggregate_Associations => Common.Message_Aggregate_Associations_Type_Id, Rflx_Null_Message_Aggregate => Common.Null_Message_Aggregate_Type_Id, Rflx_Checksum_Val => Common.Checksum_Val_Type_Id, Rflx_Checksum_Value_Range => Common.Checksum_Value_Range_Type_Id, Rflx_Byte_Order_Type_Highorderfirst => Common.Byte_Order_Type_Highorderfirst_Type_Id, Rflx_Byte_Order_Type_Loworderfirst => Common.Byte_Order_Type_Loworderfirst_Type_Id, Rflx_Readable => Common.Readable_Type_Id, Rflx_Writable => Common.Writable_Type_Id, Rflx_Checksum_Assoc => Common.Checksum_Assoc_Type_Id, Rflx_Refinement_Decl => Common.Refinement_Decl_Type_Id, Rflx_Session_Decl => Common.Session_Decl_Type_Id, Rflx_Type_Decl => Common.Type_Decl_Type_Id, Rflx_Description => Common.Description_Type_Id, Rflx_Element_Value_Assoc => Common.Element_Value_Assoc_Type_Id, Rflx_Attribute => Common.Attribute_Type_Id, Rflx_Bin_Op => Common.Bin_Op_Type_Id, Rflx_Binding => Common.Binding_Type_Id, Rflx_Call => Common.Call_Type_Id, Rflx_Case_Expression => Common.Case_Expression_Type_Id, Rflx_Choice => Common.Choice_Type_Id, Rflx_Comprehension => Common.Comprehension_Type_Id, Rflx_Context_Item => Common.Context_Item_Type_Id, Rflx_Conversion => Common.Conversion_Type_Id, Rflx_Message_Aggregate => Common.Message_Aggregate_Type_Id, Rflx_Negation => Common.Negation_Type_Id, Rflx_Numeric_Literal => Common.Numeric_Literal_Type_Id, Rflx_Paren_Expression => Common.Paren_Expression_Type_Id, Rflx_Quantified_Expression => Common.Quantified_Expression_Type_Id, Rflx_Select_Node => Common.Select_Node_Type_Id, Rflx_Concatenation => Common.Concatenation_Type_Id, Rflx_Sequence_Aggregate => Common.Sequence_Aggregate_Type_Id, Rflx_String_Literal => Common.String_Literal_Type_Id, Rflx_Variable => Common.Variable_Type_Id, Rflx_Formal_Channel_Decl => Common.Formal_Channel_Decl_Type_Id, Rflx_Formal_Function_Decl => Common.Formal_Function_Decl_Type_Id, Rflx_Renaming_Decl => Common.Renaming_Decl_Type_Id, Rflx_Variable_Decl => Common.Variable_Decl_Type_Id, Rflx_Message_Aggregate_Association => Common.Message_Aggregate_Association_Type_Id, Rflx_Byte_Order_Aspect => Common.Byte_Order_Aspect_Type_Id, Rflx_Checksum_Aspect => Common.Checksum_Aspect_Type_Id, Rflx_Message_Field => Common.Message_Field_Type_Id, Rflx_Message_Fields => Common.Message_Fields_Type_Id, Rflx_Null_Message_Field => Common.Null_Message_Field_Type_Id, Rflx_Op_Add => Common.Op_Add_Type_Id, Rflx_Op_And => Common.Op_And_Type_Id, Rflx_Op_Div => Common.Op_Div_Type_Id, Rflx_Op_Eq => Common.Op_Eq_Type_Id, Rflx_Op_Ge => Common.Op_Ge_Type_Id, Rflx_Op_Gt => Common.Op_Gt_Type_Id, Rflx_Op_In => Common.Op_In_Type_Id, Rflx_Op_Le => Common.Op_Le_Type_Id, Rflx_Op_Lt => Common.Op_Lt_Type_Id, Rflx_Op_Mod => Common.Op_Mod_Type_Id, Rflx_Op_Mul => Common.Op_Mul_Type_Id, Rflx_Op_Neq => Common.Op_Neq_Type_Id, Rflx_Op_Notin => Common.Op_Notin_Type_Id, Rflx_Op_Or => Common.Op_Or_Type_Id, Rflx_Op_Pow => Common.Op_Pow_Type_Id, Rflx_Op_Sub => Common.Op_Sub_Type_Id, Rflx_Package_Node => Common.Package_Node_Type_Id, Rflx_Parameter => Common.Parameter_Type_Id, Rflx_Parameters => Common.Parameters_Type_Id, Rflx_Quantifier_All => Common.Quantifier_All_Type_Id, Rflx_Quantifier_Some => Common.Quantifier_Some_Type_Id, Rflx_Aspect_List => Common.Aspect_List_Type_Id, Rflx_Base_Checksum_Val_List => Common.Base_Checksum_Val_List_Type_Id, Rflx_Channel_Attribute_List => Common.Channel_Attribute_List_Type_Id, Rflx_Checksum_Assoc_List => Common.Checksum_Assoc_List_Type_Id, Rflx_Choice_List => Common.Choice_List_Type_Id, Rflx_Conditional_Transition_List => Common.Conditional_Transition_List_Type_Id, Rflx_Context_Item_List => Common.Context_Item_List_Type_Id, Rflx_Declaration_List => Common.Declaration_List_Type_Id, Rflx_Element_Value_Assoc_List => Common.Element_Value_Assoc_List_Type_Id, Rflx_Expr_List => Common.Expr_List_Type_Id, Rflx_Formal_Decl_List => Common.Formal_Decl_List_Type_Id, Rflx_Local_Decl_List => Common.Local_Decl_List_Type_Id, Rflx_Message_Aggregate_Association_List => Common.Message_Aggregate_Association_List_Type_Id, Rflx_Message_Aspect_List => Common.Message_Aspect_List_Type_Id, Rflx_Message_Field_List => Common.Message_Field_List_Type_Id, Rflx_Numeric_Literal_List => Common.Numeric_Literal_List_Type_Id, Rflx_Parameter_List => Common.Parameter_List_Type_Id, Rflx_R_F_L_X_Node_List => Common.R_F_L_X_Node_List_Type_Id, Rflx_State_List => Common.State_List_Type_Id, Rflx_Statement_List => Common.Statement_List_Type_Id, Rflx_Term_Assoc_List => Common.Term_Assoc_List_Type_Id, Rflx_Then_Node_List => Common.Then_Node_List_Type_Id, Rflx_Type_Argument_List => Common.Type_Argument_List_Type_Id, Rflx_Unqualified_I_D_List => Common.Unqualified_I_D_List_Type_Id, Rflx_Specification => Common.Specification_Type_Id, Rflx_State => Common.State_Type_Id, Rflx_State_Body => Common.State_Body_Type_Id, Rflx_Assignment => Common.Assignment_Type_Id, Rflx_Attribute_Statement => Common.Attribute_Statement_Type_Id, Rflx_Message_Field_Assignment => Common.Message_Field_Assignment_Type_Id, Rflx_Reset => Common.Reset_Type_Id, Rflx_Term_Assoc => Common.Term_Assoc_Type_Id, Rflx_Then_Node => Common.Then_Node_Type_Id, Rflx_Transition => Common.Transition_Type_Id, Rflx_Conditional_Transition => Common.Conditional_Transition_Type_Id, Rflx_Type_Argument => Common.Type_Argument_Type_Id, Rflx_Message_Type_Def => Common.Message_Type_Def_Type_Id, Rflx_Null_Message_Type_Def => Common.Null_Message_Type_Def_Type_Id, Rflx_Named_Enumeration_Def => Common.Named_Enumeration_Def_Type_Id, Rflx_Positional_Enumeration_Def => Common.Positional_Enumeration_Def_Type_Id, Rflx_Enumeration_Type_Def => Common.Enumeration_Type_Def_Type_Id, Rflx_Modular_Type_Def => Common.Modular_Type_Def_Type_Id, Rflx_Range_Type_Def => Common.Range_Type_Def_Type_Id, Rflx_Sequence_Type_Def => Common.Sequence_Type_Def_Type_Id, Rflx_Type_Derivation_Def => Common.Type_Derivation_Def_Type_Id
   );

   ------------------
   -- Struct types --
   ------------------

   function Struct_Type_Desc
     (Kind : Struct_Value_Kind) return Struct_Type_Descriptor_Access;
   --  Return the type descriptor corresponding to the given struct type

   function Struct_Field_Name
     (Field : Struct_Field_Reference) return Text_Type;
   --  Helper for Member_Name: take care of structs

   function Struct_Field_Type
     (Field : Struct_Field_Reference) return Type_Constraint;
   --  Helper for Member_Type: take care of structs

   function Struct_Fields
     (Kind : Struct_Value_Kind) return Struct_Field_Reference_Array;
   --  Implementation for Introspection.Struct_Fields

   ----------------
   -- Node types --
   ----------------

   function DSL_Name (Id : Node_Type_Id) return Text_Type;
   --  Implementation for Introspection.DSL_Name

   function Lookup_DSL_Name (Name : Text_Type) return Any_Node_Type_Id;
   --  Implementation for Introspection.Lookup_DSL_Name

   function Is_Abstract (Id : Node_Type_Id) return Boolean;
   --  Implementation for Introspection.Is_Abstract

   function Is_Concrete (Id : Node_Type_Id) return Boolean
   is (not Is_Abstract (Id));

   function Kind_For (Id : Node_Type_Id) return R_F_L_X_Node_Kind_Type;
   --  Implementation for Introspection.Kind_For

   function First_Kind_For (Id : Node_Type_Id) return R_F_L_X_Node_Kind_Type;
   --  Implementation for Introspection.First_Kind_For

   function Last_Kind_For (Id : Node_Type_Id) return R_F_L_X_Node_Kind_Type;
   --  Implementation for Introspection.Last_Kind_For

   function Id_For_Kind (Kind : R_F_L_X_Node_Kind_Type) return Node_Type_Id;
   --  Implementation for Introspection.Id_For_Kind

   function Is_Root_Node (Id : Node_Type_Id) return Boolean;
   --  Implementation for Introspection.Is_Root_NOde

   function Base_Type (Id : Node_Type_Id) return Node_Type_Id;
   --  Implementation for Introspection.Base_Type

   function Derived_Types (Id : Node_Type_Id) return Node_Type_Id_Array;
   --  Implementation for Introspection.Derived_Types

   function Is_Derived_From (Id, Parent : Node_Type_Id) return Boolean;
   --  Implementation for Introspection.Is_Derived_From

   ------------
   -- Member --
   ------------

   function Member_Name (Member : Member_Reference) return Text_Type;
   --  Implementation for Introspection.Member_Name

   function Member_Type (Member : Member_Reference) return Type_Constraint;
   --  Implementation for Introspection.Member_Type

   function Lookup_Member_Struct
     (Kind : Struct_Value_Kind;
      Name : Text_Type) return Any_Member_Reference;
   --  Helper for Introspection.Lookup_Member: take care of struct types

   function Lookup_Member_Node
     (Id   : Node_Type_Id;
      Name : Text_Type) return Any_Member_Reference;
   --  Helper for Introspection.Lookup_Member: take care of nodes

   -------------------
   -- Syntax fields --
   -------------------

   function Syntax_Field_Name
     (Field : Syntax_Field_Reference) return Text_Type;
   --  Helper for Member_Name: take care of syntax fields

   function Syntax_Field_Type
     (Field : Syntax_Field_Reference) return Node_Type_Id;
   --  Helper for Member_Type: take care of syntax fields

   function Eval_Syntax_Field
     (Node  : Bare_R_F_L_X_Node;
      Field : Syntax_Field_Reference) return Bare_R_F_L_X_Node;
   --  Implementation for Introspection.Eval_Field

   function Index
     (Kind : R_F_L_X_Node_Kind_Type; Field : Syntax_Field_Reference) return Positive;
   --  Implementation for Introspection.Index

   function Syntax_Field_Reference_From_Index
     (Kind : R_F_L_X_Node_Kind_Type; Index : Positive) return Syntax_Field_Reference;
   --  Implementation for Introspection.Syntax_Field_Reference_From_Index

   function Syntax_Fields
     (Id            : Node_Type_Id;
      Concrete_Only : Boolean) return Syntax_Field_Reference_Array;
   --  Return the list of fields associated to ``Id``. If ``Concrete_Only`` is
   --  true, collect only non-null and concrete fields. Otherwise, collect all
   --  fields.

   function Syntax_Fields
     (Kind : R_F_L_X_Node_Kind_Type) return Syntax_Field_Reference_Array;
   --  Implementation for Introspection.Fields

   function Syntax_Fields
     (Id : Node_Type_Id) return Syntax_Field_Reference_Array;
   --  Implementation for Introspection.Fields

   ----------------
   -- Properties --
   ----------------

   function Property_Name (Property : Property_Reference) return Text_Type;
   --  Helper for Member_Name: take care of properties

   function Property_Return_Type
     (Property : Property_Reference) return Type_Constraint;
   --  Helper for Member_Type: take care of properties

   function Property_Argument_Types
     (Property : Property_Reference) return Type_Constraint_Array;
   --  Implementation for Introspection.Property_Argument_Types

   function Property_Argument_Name
     (Property        : Property_Reference;
      Argument_Number : Positive) return Text_Type;
   --  Implementation for Introspection.Property_Argument_Name

   function Property_Argument_Default_Value
     (Property        : Property_Reference;
      Argument_Number : Positive) return Internal_Value;
   --  Implementation for Introspection.Property_Argument_Default_Value

   function Properties (Kind : R_F_L_X_Node_Kind_Type) return Property_Reference_Array;
   --  Implementation for Introspection.Properties

   function Properties (Id : Node_Type_Id) return Property_Reference_Array;
   --  Implementation for Introspection.Properties

   procedure Check_Argument_Number
     (Desc : Property_Descriptor; Argument_Number : Positive);
   --  Raise a ``Property_Error`` if ``Argument_Number`` is not valid for the
   --  property that ``Desc`` describes. Do nothing otherwise.


   ------------
   -- Tokens --
   ------------

   function Token_Node_Kind (Kind : R_F_L_X_Node_Kind_Type) return Token_Kind;
   --  Implementation for Introspection.Token_Node_Kind

end Librflxlang.Introspection_Implementation;
