


package body Librflxlang.Lexer_State_Machine is

   Is_Trivia : constant array (Token_Kind) of Boolean := (
      Rflx_Termination => False, Rflx_Lexing_Failure => True, Rflx_Unqualified_Identifier => False, Rflx_Package => False, Rflx_Is => False, Rflx_If => False, Rflx_End => False, Rflx_Null => False, Rflx_Type => False, Rflx_Range => False, Rflx_With => False, Rflx_Mod => False, Rflx_Message => False, Rflx_Then => False, Rflx_Sequence => False, Rflx_Of => False, Rflx_In => False, Rflx_Not => False, Rflx_New => False, Rflx_For => False, Rflx_When => False, Rflx_Where => False, Rflx_Use => False, Rflx_All => False, Rflx_Some => False, Rflx_Generic => False, Rflx_Session => False, Rflx_Begin => False, Rflx_Return => False, Rflx_Function => False, Rflx_State => False, Rflx_Transition => False, Rflx_Goto => False, Rflx_Exception => False, Rflx_Renames => False, Rflx_Channel => False, Rflx_Readable => False, Rflx_Writable => False, Rflx_Desc => False, Rflx_Append => False, Rflx_Extend => False, Rflx_Read => False, Rflx_Write => False, Rflx_Reset => False, Rflx_High_Order_First => False, Rflx_Low_Order_First => False, Rflx_Case => False, Rflx_First => False, Rflx_Size => False, Rflx_Last => False, Rflx_Byte_Order => False, Rflx_Checksum => False, Rflx_Valid_Checksum => False, Rflx_Has_Data => False, Rflx_Head => False, Rflx_Opaque => False, Rflx_Present => False, Rflx_Valid => False, Rflx_Dot => False, Rflx_Comma => False, Rflx_Double_Dot => False, Rflx_Tick => False, Rflx_Hash => False, Rflx_Minus => False, Rflx_Arrow => False, Rflx_L_Par => False, Rflx_R_Par => False, Rflx_L_Brack => False, Rflx_R_Brack => False, Rflx_Exp => False, Rflx_Mul => False, Rflx_Div => False, Rflx_Add => False, Rflx_Sub => False, Rflx_Eq => False, Rflx_Neq => False, Rflx_Leq => False, Rflx_Lt => False, Rflx_Le => False, Rflx_Gt => False, Rflx_Ge => False, Rflx_And => False, Rflx_Or => False, Rflx_Ampersand => False, Rflx_Semicolon => False, Rflx_Double_Colon => False, Rflx_Assignment => False, Rflx_Colon => False, Rflx_Pipe => False, Rflx_Comment => True, Rflx_Numeral => False, Rflx_String_Literal => False
   );

   type Character_Range is record
      First, Last : Character_Type;
   end record;

   type Character_Range_Array is array (Positive range <>) of Character_Range;
   --  Sorted list of dijoint character ranges

   pragma Warnings (Off, "referenced");
   function Contains
     (Char : Character_Type; Ranges : Character_Range_Array) return Boolean;
   --  Return whether Char is included in the given ranges
   pragma Warnings (On, "referenced");

   ----------------
   -- Initialize --
   ----------------

   procedure Initialize
     (Self        : out Lexer_State;
      Input       : Text_Access;
      Input_First : Positive;
      Input_Last  : Natural) is
   begin
      Self.Input := Input;
      Self.Input_First := Input_First;
      Self.Input_Last := Input_Last;
      Self.Has_Next := True;
      Self.Last_Token := (Kind       => Rflx_Termination,
                          Text_First => Input_First,
                          Text_Last  => Input_First - 1);
      Self.Last_Token_Kind := Rflx_Termination;
   end Initialize;

   ----------------
   -- Last_Token --
   ----------------

   function Last_Token (Self : Lexer_State) return Lexed_Token is
   begin
      return Self.Last_Token;
   end Last_Token;

   --------------
   -- Has_Next --
   --------------

   function Has_Next (Self : Lexer_State) return Boolean is
   begin
      return Self.Has_Next;
   end Has_Next;

   --------------
   -- Contains --
   --------------

   function Contains
     (Char : Character_Type; Ranges : Character_Range_Array) return Boolean
   is
      Low  : Natural := Ranges'First;
      High : Natural := Ranges'Last;
   begin
      while Low <= High loop
         declare
            Middle : constant Natural := (Low + High) / 2;
            R      : Character_Range renames Ranges (Middle);
         begin
            if Char < R.First then
               High := Middle - 1;
            elsif Char > R.Last then
               Low := Middle + 1;
            else
               return True;
            end if;
         end;
      end loop;
      return False;
   end Contains;



   ----------------
   -- Next_Token --
   ----------------

   procedure Next_Token
     (Self : in out Lexer_State; Token : out Lexed_Token)
   is
      Input : constant Text_Access := Self.Input;

      First_Index : Positive;
      --  Index of the first input character for the token to return

      Index : Positive;
      --  Index for the next input character to be analyzed

      Match_Index : Natural;
      --  If we found a match, index for its last character. Otherwise, zero.

      Match_Ignore : Boolean;
      --  If we found a match, whether we must ignore it and restart the
      --  automaton after its character range.

      Match_Kind : Token_Kind;
      --  If we found a match and it is not ignored, kind for the token to
      --  emit. Meaningless otherwise.
   begin
      First_Index := Self.Last_Token.Text_Last + 1;

      <<Start>>
      Index := First_Index;
      Match_Index := 0;
      Match_Ignore := False;



         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when Character_Type'Val (16#9#) .. Character_Type'Val (16#a#) | Character_Type'Val (16#d#) | ' ' => goto State_1;
               when '"' => goto State_2;
               when '#' => goto State_3;
               when '&' => goto State_4;
               when ''' => goto State_5;
               when '(' => goto State_6;
               when ')' => goto State_7;
               when '*' => goto State_8;
               when '+' => goto State_9;
               when ',' => goto State_10;
               when '-' => goto State_11;
               when '.' => goto State_12;
               when '/' => goto State_13;
               when '0' .. '9' => goto State_14;
               when ':' => goto State_15;
               when ';' => goto State_16;
               when '<' => goto State_17;
               when '=' => goto State_18;
               when '>' => goto State_19;
               when 'A' => goto State_20;
               when 'B' .. 'A' | 'C' .. 'B' | 'D' .. 'C' | 'E' .. 'D' | 'F' .. 'E' | 'G' | 'I' .. 'K' | 'M' .. 'N' | 'P' .. 'O' | 'Q' | 'S' .. 'R' | 'T' .. 'U' | 'W' .. 'V' | 'X' .. 'Z' | 'b' .. 'a' | 'c' .. 'b' | 'd' | 'f' .. 'e' | 'g' .. 'f' | 'h' | 'j' .. 'l' | 'n' .. 'm' | 'o' .. 'n' | 'p' .. 'o' | 'q' | 's' .. 'r' | 't' .. 's' | 'u' .. 't' | 'v' | 'x' .. 'z' => goto State_21;
               when 'B' => goto State_22;
               when 'C' => goto State_23;
               when 'D' => goto State_24;
               when 'E' => goto State_25;
               when 'F' => goto State_26;
               when 'H' => goto State_27;
               when 'L' => goto State_28;
               when 'O' => goto State_29;
               when 'P' => goto State_30;
               when 'R' => goto State_31;
               when 'S' => goto State_32;
               when 'V' => goto State_33;
               when 'W' => goto State_34;
               when '[' => goto State_35;
               when ']' => goto State_36;
               when 'a' => goto State_37;
               when 'b' => goto State_38;
               when 'c' => goto State_39;
               when 'e' => goto State_40;
               when 'f' => goto State_41;
               when 'g' => goto State_42;
               when 'i' => goto State_43;
               when 'm' => goto State_44;
               when 'n' => goto State_45;
               when 'o' => goto State_46;
               when 'p' => goto State_47;
               when 'r' => goto State_48;
               when 's' => goto State_49;
               when 't' => goto State_50;
               when 'u' => goto State_51;
               when 'w' => goto State_52;
               when '|' => goto State_53;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_1>>

               Match_Index := Index - 1;
               Match_Ignore := True;


         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when Character_Type'Val (16#9#) .. Character_Type'Val (16#a#) | Character_Type'Val (16#d#) | ' ' => goto State_54;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_2>>


         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when Character_Type'Val (16#0#) .. '!' | '#' .. Character_Type'Val (16#10ffff#) => goto State_55;
               when '"' => goto State_56;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_3>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Hash;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         Index := Index + 1;
         goto Stop;

            <<State_4>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Ampersand;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         Index := Index + 1;
         goto Stop;

            <<State_5>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Tick;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         Index := Index + 1;
         goto Stop;

            <<State_6>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_L_Par;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         Index := Index + 1;
         goto Stop;

            <<State_7>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_R_Par;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         Index := Index + 1;
         goto Stop;

            <<State_8>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Mul;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '*' => goto State_57;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_9>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Add;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         Index := Index + 1;
         goto Stop;

            <<State_10>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Comma;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         Index := Index + 1;
         goto Stop;

            <<State_11>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Sub;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '-' => goto State_58;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_12>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Dot;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '.' => goto State_59;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_13>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Div;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '=' => goto State_60;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_14>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Numeral;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '#' => goto State_61;
               when '0' .. '9' => goto State_62;
               when '_' => goto State_63;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_15>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Colon;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when ':' => goto State_64;
               when '=' => goto State_65;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_16>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Semicolon;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         Index := Index + 1;
         goto Stop;

            <<State_17>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Lt;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '=' => goto State_66;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_18>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Eq;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '>' => goto State_67;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_19>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Gt;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '=' => goto State_68;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_20>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'o' | 'q' .. 'z' => goto State_69;
               when 'p' => goto State_70;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_21>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'z' => goto State_69;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_22>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'x' | 'z' => goto State_69;
               when 'y' => goto State_71;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_23>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'g' | 'i' .. 'z' => goto State_69;
               when 'h' => goto State_72;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_24>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'd' | 'f' .. 'z' => goto State_69;
               when 'e' => goto State_73;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_25>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'w' | 'y' .. 'z' => goto State_69;
               when 'x' => goto State_74;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_26>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'h' | 'j' .. 'z' => goto State_69;
               when 'i' => goto State_75;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_27>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'b' .. 'd' | 'f' .. 'h' | 'j' .. 'z' => goto State_69;
               when 'a' => goto State_76;
               when 'e' => goto State_77;
               when 'i' => goto State_78;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_28>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'b' .. 'n' | 'p' .. 'z' => goto State_69;
               when 'a' => goto State_79;
               when 'o' => goto State_80;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_29>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'o' | 'q' .. 'z' => goto State_69;
               when 'p' => goto State_81;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_30>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'q' | 's' .. 'z' => goto State_69;
               when 'r' => goto State_82;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_31>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'd' | 'f' .. 'z' => goto State_69;
               when 'e' => goto State_83;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_32>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'h' | 'j' .. 'z' => goto State_69;
               when 'i' => goto State_84;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_33>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'b' .. 'z' => goto State_69;
               when 'a' => goto State_85;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_34>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'q' | 's' .. 'z' => goto State_69;
               when 'r' => goto State_86;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_35>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_L_Brack;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         Index := Index + 1;
         goto Stop;

            <<State_36>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_R_Brack;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         Index := Index + 1;
         goto Stop;

            <<State_37>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'k' | 'm' | 'o' .. 'z' => goto State_69;
               when 'l' => goto State_87;
               when 'n' => goto State_88;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_38>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'd' | 'f' .. 'z' => goto State_69;
               when 'e' => goto State_89;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_39>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'b' .. 'z' => goto State_69;
               when 'a' => goto State_90;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_40>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'm' | 'o' .. 'w' | 'y' .. 'z' => goto State_69;
               when 'n' => goto State_91;
               when 'x' => goto State_92;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_41>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'n' | 'p' .. 't' | 'v' .. 'z' => goto State_69;
               when 'o' => goto State_93;
               when 'u' => goto State_94;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_42>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'd' | 'f' .. 'n' | 'p' .. 'z' => goto State_69;
               when 'e' => goto State_95;
               when 'o' => goto State_96;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_43>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'e' | 'g' .. 'm' | 'o' .. 'r' | 't' .. 'z' => goto State_69;
               when 'f' => goto State_97;
               when 'n' => goto State_98;
               when 's' => goto State_99;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_44>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'd' | 'f' .. 'n' | 'p' .. 'z' => goto State_69;
               when 'e' => goto State_100;
               when 'o' => goto State_101;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_45>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'd' | 'f' .. 'n' | 'p' .. 't' | 'v' .. 'z' => goto State_69;
               when 'e' => goto State_102;
               when 'o' => goto State_103;
               when 'u' => goto State_104;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_46>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'e' | 'g' .. 'q' | 's' .. 'z' => goto State_69;
               when 'f' => goto State_105;
               when 'r' => goto State_106;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_47>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'b' .. 'z' => goto State_69;
               when 'a' => goto State_107;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_48>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'b' .. 'd' | 'f' .. 'z' => goto State_69;
               when 'a' => goto State_108;
               when 'e' => goto State_109;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_49>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'd' | 'f' .. 'n' | 'p' .. 's' | 'u' .. 'z' => goto State_69;
               when 'e' => goto State_110;
               when 'o' => goto State_111;
               when 't' => goto State_112;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_50>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'g' | 'i' .. 'q' | 's' .. 'x' | 'z' => goto State_69;
               when 'h' => goto State_113;
               when 'r' => goto State_114;
               when 'y' => goto State_115;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_51>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'r' | 't' .. 'z' => goto State_69;
               when 's' => goto State_116;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_52>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'g' | 'i' .. 'h' | 'j' .. 'z' => goto State_69;
               when 'h' => goto State_117;
               when 'i' => goto State_118;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_53>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Pipe;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         Index := Index + 1;
         goto Stop;

            <<State_54>>

               Match_Index := Index - 1;
               Match_Ignore := True;


         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when Character_Type'Val (16#9#) .. Character_Type'Val (16#a#) | Character_Type'Val (16#d#) | ' ' => goto State_54;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_55>>


         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when Character_Type'Val (16#0#) .. '!' | '#' .. Character_Type'Val (16#10ffff#) => goto State_55;
               when '"' => goto State_56;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_56>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_String_Literal;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         Index := Index + 1;
         goto Stop;

            <<State_57>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Exp;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         Index := Index + 1;
         goto Stop;

            <<State_58>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Comment;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when Character_Type'Val (16#0#) .. Character_Type'Val (16#9#) | Character_Type'Val (16#b#) .. Character_Type'Val (16#10ffff#) => goto State_119;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_59>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Double_Dot;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         Index := Index + 1;
         goto Stop;

            <<State_60>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Neq;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         Index := Index + 1;
         goto Stop;

            <<State_61>>


         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'F' => goto State_120;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_62>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Numeral;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '#' => goto State_61;
               when '0' .. '9' => goto State_121;
               when '_' => goto State_63;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_63>>


         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' => goto State_122;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_64>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Double_Colon;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         Index := Index + 1;
         goto Stop;

            <<State_65>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Assignment;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         Index := Index + 1;
         goto Stop;

            <<State_66>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Le;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         Index := Index + 1;
         goto Stop;

            <<State_67>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Arrow;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         Index := Index + 1;
         goto Stop;

            <<State_68>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Ge;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         Index := Index + 1;
         goto Stop;

            <<State_69>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'z' => goto State_69;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_70>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'o' | 'q' .. 'z' => goto State_69;
               when 'p' => goto State_123;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_71>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 's' | 'u' .. 'z' => goto State_69;
               when 't' => goto State_124;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_72>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'b' .. 'd' | 'f' .. 'z' => goto State_69;
               when 'a' => goto State_125;
               when 'e' => goto State_126;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_73>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'r' | 't' .. 'z' => goto State_69;
               when 's' => goto State_127;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_74>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 's' | 'u' .. 'z' => goto State_69;
               when 't' => goto State_128;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_75>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'q' | 's' .. 'z' => goto State_69;
               when 'r' => goto State_129;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_76>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'r' | 't' .. 'z' => goto State_69;
               when 's' => goto State_130;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_77>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'b' .. 'z' => goto State_69;
               when 'a' => goto State_131;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_78>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'f' | 'h' .. 'z' => goto State_69;
               when 'g' => goto State_132;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_79>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'r' | 't' .. 'z' => goto State_69;
               when 's' => goto State_133;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_80>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'v' | 'x' .. 'z' => goto State_69;
               when 'w' => goto State_134;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_81>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'b' .. 'z' => goto State_69;
               when 'a' => goto State_135;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_82>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'd' | 'f' .. 'z' => goto State_69;
               when 'e' => goto State_136;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_83>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'b' .. 'r' | 't' .. 'z' => goto State_69;
               when 'a' => goto State_137;
               when 's' => goto State_138;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_84>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'y' => goto State_69;
               when 'z' => goto State_139;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_85>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'k' | 'm' .. 'z' => goto State_69;
               when 'l' => goto State_140;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_86>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'h' | 'j' .. 'z' => goto State_69;
               when 'i' => goto State_141;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_87>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'k' | 'm' .. 'z' => goto State_69;
               when 'l' => goto State_142;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_88>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'c' | 'e' .. 'z' => goto State_69;
               when 'd' => goto State_143;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_89>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'f' | 'h' .. 'z' => goto State_69;
               when 'g' => goto State_144;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_90>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'r' | 't' .. 'z' => goto State_69;
               when 's' => goto State_145;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_91>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'c' | 'e' .. 'z' => goto State_69;
               when 'd' => goto State_146;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_92>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'b' | 'd' .. 'z' => goto State_69;
               when 'c' => goto State_147;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_93>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'q' | 's' .. 'z' => goto State_69;
               when 'r' => goto State_148;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_94>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'm' | 'o' .. 'z' => goto State_69;
               when 'n' => goto State_149;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_95>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'm' | 'o' .. 'z' => goto State_69;
               when 'n' => goto State_150;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_96>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 's' | 'u' .. 'z' => goto State_69;
               when 't' => goto State_151;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_97>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_If;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'z' => goto State_69;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_98>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_In;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'z' => goto State_69;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_99>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Is;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'z' => goto State_69;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_100>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'r' | 't' .. 'z' => goto State_69;
               when 's' => goto State_152;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_101>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'c' | 'e' .. 'z' => goto State_69;
               when 'd' => goto State_153;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_102>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'v' | 'x' .. 'z' => goto State_69;
               when 'w' => goto State_154;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_103>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 's' | 'u' .. 'z' => goto State_69;
               when 't' => goto State_155;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_104>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'k' | 'm' .. 'z' => goto State_69;
               when 'l' => goto State_156;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_105>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Of;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'z' => goto State_69;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_106>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Or;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'z' => goto State_69;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_107>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'b' | 'd' .. 'z' => goto State_69;
               when 'c' => goto State_157;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_108>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'm' | 'o' .. 'z' => goto State_69;
               when 'n' => goto State_158;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_109>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'm' | 'o' .. 's' | 'u' .. 'z' => goto State_69;
               when 'n' => goto State_159;
               when 't' => goto State_160;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_110>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'p' | 'r' | 't' .. 'z' => goto State_69;
               when 'q' => goto State_161;
               when 's' => goto State_162;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_111>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'l' | 'n' .. 'z' => goto State_69;
               when 'm' => goto State_163;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_112>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'b' .. 'z' => goto State_69;
               when 'a' => goto State_164;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_113>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'd' | 'f' .. 'z' => goto State_69;
               when 'e' => goto State_165;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_114>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'b' .. 'z' => goto State_69;
               when 'a' => goto State_166;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_115>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'o' | 'q' .. 'z' => goto State_69;
               when 'p' => goto State_167;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_116>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'd' | 'f' .. 'z' => goto State_69;
               when 'e' => goto State_168;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_117>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'd' | 'f' .. 'z' => goto State_69;
               when 'e' => goto State_169;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_118>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 's' | 'u' .. 'z' => goto State_69;
               when 't' => goto State_170;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_119>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Comment;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when Character_Type'Val (16#0#) .. Character_Type'Val (16#9#) | Character_Type'Val (16#b#) .. Character_Type'Val (16#10ffff#) => goto State_119;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_120>>


         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '#' => goto State_171;
               when '0' .. '9' | 'A' .. 'F' => goto State_172;
               when '_' => goto State_173;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_121>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Numeral;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '#' => goto State_61;
               when '0' .. '9' => goto State_121;
               when '_' => goto State_63;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_122>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Numeral;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' => goto State_174;
               when '_' => goto State_63;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_123>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'd' | 'f' .. 'z' => goto State_69;
               when 'e' => goto State_175;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_124>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'd' | 'f' .. 'z' => goto State_69;
               when 'e' => goto State_176;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_125>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'm' | 'o' .. 'z' => goto State_69;
               when 'n' => goto State_177;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_126>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'b' | 'd' .. 'z' => goto State_69;
               when 'c' => goto State_178;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_127>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'b' | 'd' .. 'z' => goto State_69;
               when 'c' => goto State_179;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_128>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'd' | 'f' .. 'z' => goto State_69;
               when 'e' => goto State_180;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_129>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'r' | 't' .. 'z' => goto State_69;
               when 's' => goto State_181;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_130>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | 'a' .. 'z' => goto State_69;
               when '_' => goto State_182;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_131>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'c' | 'e' .. 'z' => goto State_69;
               when 'd' => goto State_183;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_132>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'g' | 'i' .. 'z' => goto State_69;
               when 'h' => goto State_184;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_133>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 's' | 'u' .. 'z' => goto State_69;
               when 't' => goto State_185;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_134>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | 'a' .. 'z' => goto State_69;
               when '_' => goto State_186;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_135>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'p' | 'r' .. 'z' => goto State_69;
               when 'q' => goto State_187;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_136>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'r' | 't' .. 'z' => goto State_69;
               when 's' => goto State_188;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_137>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'c' | 'e' .. 'z' => goto State_69;
               when 'd' => goto State_189;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_138>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'd' | 'f' .. 'z' => goto State_69;
               when 'e' => goto State_190;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_139>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'd' | 'f' .. 'z' => goto State_69;
               when 'e' => goto State_191;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_140>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'h' | 'j' .. 'z' => goto State_69;
               when 'i' => goto State_192;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_141>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 's' | 'u' .. 'z' => goto State_69;
               when 't' => goto State_193;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_142>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_All;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'z' => goto State_69;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_143>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_And;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'z' => goto State_69;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_144>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'h' | 'j' .. 'z' => goto State_69;
               when 'i' => goto State_194;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_145>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'd' | 'f' .. 'z' => goto State_69;
               when 'e' => goto State_195;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_146>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_End;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'z' => goto State_69;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_147>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'd' | 'f' .. 'z' => goto State_69;
               when 'e' => goto State_196;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_148>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_For;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'z' => goto State_69;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_149>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'b' | 'd' .. 'z' => goto State_69;
               when 'c' => goto State_197;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_150>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'd' | 'f' .. 'z' => goto State_69;
               when 'e' => goto State_198;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_151>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'n' | 'p' .. 'z' => goto State_69;
               when 'o' => goto State_199;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_152>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'r' | 't' .. 'z' => goto State_69;
               when 's' => goto State_200;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_153>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Mod;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'z' => goto State_69;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_154>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_New;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'z' => goto State_69;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_155>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Not;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'z' => goto State_69;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_156>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'k' | 'm' .. 'z' => goto State_69;
               when 'l' => goto State_201;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_157>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'j' | 'l' .. 'z' => goto State_69;
               when 'k' => goto State_202;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_158>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'f' | 'h' .. 'z' => goto State_69;
               when 'g' => goto State_203;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_159>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'b' .. 'z' => goto State_69;
               when 'a' => goto State_204;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_160>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 't' | 'v' .. 'z' => goto State_69;
               when 'u' => goto State_205;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_161>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 't' | 'v' .. 'z' => goto State_69;
               when 'u' => goto State_206;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_162>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'r' | 't' .. 'z' => goto State_69;
               when 's' => goto State_207;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_163>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'd' | 'f' .. 'z' => goto State_69;
               when 'e' => goto State_208;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_164>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 's' | 'u' .. 'z' => goto State_69;
               when 't' => goto State_209;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_165>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'm' | 'o' .. 'z' => goto State_69;
               when 'n' => goto State_210;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_166>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'm' | 'o' .. 'z' => goto State_69;
               when 'n' => goto State_211;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_167>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'd' | 'f' .. 'z' => goto State_69;
               when 'e' => goto State_212;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_168>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Use;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'z' => goto State_69;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_169>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'm' | 'o' .. 'q' | 's' .. 'z' => goto State_69;
               when 'n' => goto State_213;
               when 'r' => goto State_214;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_170>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'g' | 'i' .. 'z' => goto State_69;
               when 'h' => goto State_215;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_171>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Numeral;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         Index := Index + 1;
         goto Stop;

            <<State_172>>


         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '#' => goto State_171;
               when '0' .. '9' | 'A' .. 'F' => goto State_216;
               when '_' => goto State_173;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_173>>


         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'F' => goto State_217;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_174>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Numeral;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' => goto State_174;
               when '_' => goto State_63;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_175>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'm' | 'o' .. 'z' => goto State_69;
               when 'n' => goto State_218;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_176>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | 'a' .. 'z' => goto State_69;
               when '_' => goto State_219;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_177>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'm' | 'o' .. 'z' => goto State_69;
               when 'n' => goto State_220;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_178>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'j' | 'l' .. 'z' => goto State_69;
               when 'k' => goto State_221;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_179>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Desc;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'z' => goto State_69;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_180>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'm' | 'o' .. 'z' => goto State_69;
               when 'n' => goto State_222;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_181>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 's' | 'u' .. 'z' => goto State_69;
               when 't' => goto State_223;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_182>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'C' | 'E' .. 'Z' | '_' | 'a' .. 'z' => goto State_69;
               when 'D' => goto State_224;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_183>>

               case Self.Last_Token_Kind is
                     when Rflx_Tick =>
                        Match_Kind := Rflx_Head;
                        Match_Index := Index - 1 - 0;
                     when others =>
                        Match_Kind := Rflx_Unqualified_Identifier;
                        Match_Index := Index - 1 - 0;
               end case;


         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'z' => goto State_69;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_184>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | 'a' .. 'z' => goto State_69;
               when '_' => goto State_225;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_185>>

               case Self.Last_Token_Kind is
                     when Rflx_Tick =>
                        Match_Kind := Rflx_Last;
                        Match_Index := Index - 1 - 0;
                     when others =>
                        Match_Kind := Rflx_Unqualified_Identifier;
                        Match_Index := Index - 1 - 0;
               end case;


         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'z' => goto State_69;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_186>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'N' | 'P' .. 'Z' | '_' | 'a' .. 'z' => goto State_69;
               when 'O' => goto State_226;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_187>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 't' | 'v' .. 'z' => goto State_69;
               when 'u' => goto State_227;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_188>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'd' | 'f' .. 'z' => goto State_69;
               when 'e' => goto State_228;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_189>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Read;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'b' .. 'z' => goto State_69;
               when 'a' => goto State_229;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_190>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 's' | 'u' .. 'z' => goto State_69;
               when 't' => goto State_230;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_191>>

               case Self.Last_Token_Kind is
                     when Rflx_Tick =>
                        Match_Kind := Rflx_Size;
                        Match_Index := Index - 1 - 0;
                     when others =>
                        Match_Kind := Rflx_Unqualified_Identifier;
                        Match_Index := Index - 1 - 0;
               end case;


         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'z' => goto State_69;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_192>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'c' | 'e' .. 'z' => goto State_69;
               when 'd' => goto State_231;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_193>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'b' .. 'd' | 'f' .. 'z' => goto State_69;
               when 'a' => goto State_232;
               when 'e' => goto State_233;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_194>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'm' | 'o' .. 'z' => goto State_69;
               when 'n' => goto State_234;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_195>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Case;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'z' => goto State_69;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_196>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'o' | 'q' .. 'z' => goto State_69;
               when 'p' => goto State_235;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_197>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 's' | 'u' .. 'z' => goto State_69;
               when 't' => goto State_236;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_198>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'q' | 's' .. 'z' => goto State_69;
               when 'r' => goto State_237;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_199>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Goto;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'z' => goto State_69;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_200>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'b' .. 'z' => goto State_69;
               when 'a' => goto State_238;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_201>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Null;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'z' => goto State_69;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_202>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'b' .. 'z' => goto State_69;
               when 'a' => goto State_239;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_203>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'd' | 'f' .. 'z' => goto State_69;
               when 'e' => goto State_240;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_204>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'l' | 'n' .. 'z' => goto State_69;
               when 'm' => goto State_241;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_205>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'q' | 's' .. 'z' => goto State_69;
               when 'r' => goto State_242;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_206>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'd' | 'f' .. 'z' => goto State_69;
               when 'e' => goto State_243;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_207>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'h' | 'j' .. 'z' => goto State_69;
               when 'i' => goto State_244;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_208>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Some;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'z' => goto State_69;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_209>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'd' | 'f' .. 'z' => goto State_69;
               when 'e' => goto State_245;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_210>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Then;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'z' => goto State_69;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_211>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'r' | 't' .. 'z' => goto State_69;
               when 's' => goto State_246;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_212>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Type;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'z' => goto State_69;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_213>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_When;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'z' => goto State_69;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_214>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'd' | 'f' .. 'z' => goto State_69;
               when 'e' => goto State_247;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_215>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_With;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'z' => goto State_69;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_216>>


         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '#' => goto State_171;
               when '0' .. '9' | 'A' .. 'F' => goto State_216;
               when '_' => goto State_173;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_217>>


         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '#' => goto State_171;
               when '0' .. '9' | 'A' .. 'F' => goto State_248;
               when '_' => goto State_173;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_218>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'c' | 'e' .. 'z' => goto State_69;
               when 'd' => goto State_249;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_219>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'N' | 'P' .. 'Z' | '_' | 'a' .. 'z' => goto State_69;
               when 'O' => goto State_250;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_220>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'd' | 'f' .. 'z' => goto State_69;
               when 'e' => goto State_251;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_221>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'r' | 't' .. 'z' => goto State_69;
               when 's' => goto State_252;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_222>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'c' | 'e' .. 'z' => goto State_69;
               when 'd' => goto State_253;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_223>>

               case Self.Last_Token_Kind is
                     when Rflx_Tick =>
                        Match_Kind := Rflx_First;
                        Match_Index := Index - 1 - 0;
                     when others =>
                        Match_Kind := Rflx_Unqualified_Identifier;
                        Match_Index := Index - 1 - 0;
               end case;


         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'z' => goto State_69;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_224>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'b' .. 'z' => goto State_69;
               when 'a' => goto State_254;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_225>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'N' | 'P' .. 'Z' | '_' | 'a' .. 'z' => goto State_69;
               when 'O' => goto State_255;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_226>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'q' | 's' .. 'z' => goto State_69;
               when 'r' => goto State_256;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_227>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'd' | 'f' .. 'z' => goto State_69;
               when 'e' => goto State_257;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_228>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'm' | 'o' .. 'z' => goto State_69;
               when 'n' => goto State_258;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_229>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' | 'c' .. 'z' => goto State_69;
               when 'b' => goto State_259;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_230>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Reset;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'z' => goto State_69;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_231>>

               case Self.Last_Token_Kind is
                     when Rflx_Tick =>
                        Match_Kind := Rflx_Valid;
                        Match_Index := Index - 1 - 0;
                     when others =>
                        Match_Kind := Rflx_Unqualified_Identifier;
                        Match_Index := Index - 1 - 0;
               end case;


         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | 'a' .. 'z' => goto State_69;
               when '_' => goto State_260;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_232>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' | 'c' .. 'z' => goto State_69;
               when 'b' => goto State_261;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_233>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Write;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'z' => goto State_69;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_234>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Begin;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'z' => goto State_69;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_235>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 's' | 'u' .. 'z' => goto State_69;
               when 't' => goto State_262;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_236>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'h' | 'j' .. 'z' => goto State_69;
               when 'i' => goto State_263;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_237>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'h' | 'j' .. 'z' => goto State_69;
               when 'i' => goto State_264;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_238>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'f' | 'h' .. 'z' => goto State_69;
               when 'g' => goto State_265;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_239>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'f' | 'h' .. 'z' => goto State_69;
               when 'g' => goto State_266;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_240>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Range;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'z' => goto State_69;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_241>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'd' | 'f' .. 'z' => goto State_69;
               when 'e' => goto State_267;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_242>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'm' | 'o' .. 'z' => goto State_69;
               when 'n' => goto State_268;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_243>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'm' | 'o' .. 'z' => goto State_69;
               when 'n' => goto State_269;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_244>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'n' | 'p' .. 'z' => goto State_69;
               when 'o' => goto State_270;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_245>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_State;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'z' => goto State_69;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_246>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'h' | 'j' .. 'z' => goto State_69;
               when 'i' => goto State_271;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_247>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Where;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'z' => goto State_69;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_248>>


         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '#' => goto State_171;
               when '0' .. '9' | 'A' .. 'F' => goto State_248;
               when '_' => goto State_173;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_249>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Append;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'z' => goto State_69;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_250>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'q' | 's' .. 'z' => goto State_69;
               when 'r' => goto State_272;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_251>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'k' | 'm' .. 'z' => goto State_69;
               when 'l' => goto State_273;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_252>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 't' | 'v' .. 'z' => goto State_69;
               when 'u' => goto State_274;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_253>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Extend;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'z' => goto State_69;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_254>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 's' | 'u' .. 'z' => goto State_69;
               when 't' => goto State_275;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_255>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'q' | 's' .. 'z' => goto State_69;
               when 'r' => goto State_276;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_256>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'c' | 'e' .. 'z' => goto State_69;
               when 'd' => goto State_277;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_257>>

               case Self.Last_Token_Kind is
                     when Rflx_Tick =>
                        Match_Kind := Rflx_Opaque;
                        Match_Index := Index - 1 - 0;
                     when others =>
                        Match_Kind := Rflx_Unqualified_Identifier;
                        Match_Index := Index - 1 - 0;
               end case;


         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'z' => goto State_69;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_258>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 's' | 'u' .. 'z' => goto State_69;
               when 't' => goto State_278;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_259>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'k' | 'm' .. 'z' => goto State_69;
               when 'l' => goto State_279;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_260>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'B' | 'D' .. 'Z' | '_' | 'a' .. 'z' => goto State_69;
               when 'C' => goto State_280;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_261>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'k' | 'm' .. 'z' => goto State_69;
               when 'l' => goto State_281;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_262>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'h' | 'j' .. 'z' => goto State_69;
               when 'i' => goto State_282;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_263>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'n' | 'p' .. 'z' => goto State_69;
               when 'o' => goto State_283;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_264>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'b' | 'd' .. 'z' => goto State_69;
               when 'c' => goto State_284;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_265>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'd' | 'f' .. 'z' => goto State_69;
               when 'e' => goto State_285;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_266>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'd' | 'f' .. 'z' => goto State_69;
               when 'e' => goto State_286;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_267>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'r' | 't' .. 'z' => goto State_69;
               when 's' => goto State_287;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_268>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Return;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'z' => goto State_69;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_269>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'b' | 'd' .. 'z' => goto State_69;
               when 'c' => goto State_288;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_270>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'm' | 'o' .. 'z' => goto State_69;
               when 'n' => goto State_289;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_271>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 's' | 'u' .. 'z' => goto State_69;
               when 't' => goto State_290;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_272>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'c' | 'e' .. 'z' => goto State_69;
               when 'd' => goto State_291;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_273>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Channel;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'z' => goto State_69;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_274>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'l' | 'n' .. 'z' => goto State_69;
               when 'm' => goto State_292;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_275>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'b' .. 'z' => goto State_69;
               when 'a' => goto State_293;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_276>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'c' | 'e' .. 'z' => goto State_69;
               when 'd' => goto State_294;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_277>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'd' | 'f' .. 'z' => goto State_69;
               when 'e' => goto State_295;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_278>>

               case Self.Last_Token_Kind is
                     when Rflx_Tick =>
                        Match_Kind := Rflx_Present;
                        Match_Index := Index - 1 - 0;
                     when others =>
                        Match_Kind := Rflx_Unqualified_Identifier;
                        Match_Index := Index - 1 - 0;
               end case;


         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'z' => goto State_69;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_279>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'd' | 'f' .. 'z' => goto State_69;
               when 'e' => goto State_296;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_280>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'g' | 'i' .. 'z' => goto State_69;
               when 'h' => goto State_297;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_281>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'd' | 'f' .. 'z' => goto State_69;
               when 'e' => goto State_298;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_282>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'n' | 'p' .. 'z' => goto State_69;
               when 'o' => goto State_299;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_283>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'm' | 'o' .. 'z' => goto State_69;
               when 'n' => goto State_300;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_284>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Generic;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'z' => goto State_69;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_285>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Message;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'z' => goto State_69;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_286>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Package;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'z' => goto State_69;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_287>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Renames;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'z' => goto State_69;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_288>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'd' | 'f' .. 'z' => goto State_69;
               when 'e' => goto State_301;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_289>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Session;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'z' => goto State_69;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_290>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'h' | 'j' .. 'z' => goto State_69;
               when 'i' => goto State_302;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_291>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'd' | 'f' .. 'z' => goto State_69;
               when 'e' => goto State_303;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_292>>

               case Self.Last_Token_Kind is
                     when Rflx_With =>
                        Match_Kind := Rflx_Checksum;
                        Match_Index := Index - 1 - 0;
                     when others =>
                        Match_Kind := Rflx_Unqualified_Identifier;
                        Match_Index := Index - 1 - 0;
               end case;


         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'z' => goto State_69;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_293>>

               case Self.Last_Token_Kind is
                     when Rflx_Tick =>
                        Match_Kind := Rflx_Has_Data;
                        Match_Index := Index - 1 - 0;
                     when others =>
                        Match_Kind := Rflx_Unqualified_Identifier;
                        Match_Index := Index - 1 - 0;
               end case;


         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'z' => goto State_69;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_294>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'd' | 'f' .. 'z' => goto State_69;
               when 'e' => goto State_304;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_295>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'q' | 's' .. 'z' => goto State_69;
               when 'r' => goto State_305;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_296>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Readable;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'z' => goto State_69;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_297>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'd' | 'f' .. 'z' => goto State_69;
               when 'e' => goto State_306;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_298>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Writable;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'z' => goto State_69;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_299>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'm' | 'o' .. 'z' => goto State_69;
               when 'n' => goto State_307;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_300>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Function;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'z' => goto State_69;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_301>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Sequence;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'z' => goto State_69;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_302>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'n' | 'p' .. 'z' => goto State_69;
               when 'o' => goto State_308;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_303>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'q' | 's' .. 'z' => goto State_69;
               when 'r' => goto State_309;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_304>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'q' | 's' .. 'z' => goto State_69;
               when 'r' => goto State_310;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_305>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | 'a' .. 'z' => goto State_69;
               when '_' => goto State_311;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_306>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'b' | 'd' .. 'z' => goto State_69;
               when 'c' => goto State_312;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_307>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Exception;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'z' => goto State_69;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_308>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'm' | 'o' .. 'z' => goto State_69;
               when 'n' => goto State_313;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_309>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Byte_Order;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'z' => goto State_69;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_310>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | 'a' .. 'z' => goto State_69;
               when '_' => goto State_314;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_311>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'E' | 'G' .. 'Z' | '_' | 'a' .. 'z' => goto State_69;
               when 'F' => goto State_315;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_312>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'j' | 'l' .. 'z' => goto State_69;
               when 'k' => goto State_316;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_313>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Transition;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'z' => goto State_69;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_314>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'E' | 'G' .. 'Z' | '_' | 'a' .. 'z' => goto State_69;
               when 'F' => goto State_317;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_315>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'h' | 'j' .. 'z' => goto State_69;
               when 'i' => goto State_318;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_316>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'r' | 't' .. 'z' => goto State_69;
               when 's' => goto State_319;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_317>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'h' | 'j' .. 'z' => goto State_69;
               when 'i' => goto State_320;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_318>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'q' | 's' .. 'z' => goto State_69;
               when 'r' => goto State_321;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_319>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 't' | 'v' .. 'z' => goto State_69;
               when 'u' => goto State_322;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_320>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'q' | 's' .. 'z' => goto State_69;
               when 'r' => goto State_323;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_321>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'r' | 't' .. 'z' => goto State_69;
               when 's' => goto State_324;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_322>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'l' | 'n' .. 'z' => goto State_69;
               when 'm' => goto State_325;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_323>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'r' | 't' .. 'z' => goto State_69;
               when 's' => goto State_326;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_324>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 's' | 'u' .. 'z' => goto State_69;
               when 't' => goto State_327;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_325>>

               case Self.Last_Token_Kind is
                     when Rflx_Tick =>
                        Match_Kind := Rflx_Valid_Checksum;
                        Match_Index := Index - 1 - 0;
                     when others =>
                        Match_Kind := Rflx_Unqualified_Identifier;
                        Match_Index := Index - 1 - 0;
               end case;


         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'z' => goto State_69;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_326>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Unqualified_Identifier;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 's' | 'u' .. 'z' => goto State_69;
               when 't' => goto State_328;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_327>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_Low_Order_First;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'z' => goto State_69;

            when others =>

               goto Stop;
            end case;
         end;

            <<State_328>>

               Match_Index := Index - 1;
               Match_Kind := Rflx_High_Order_First;

         if Index > Self.Input_Last then
            goto Stop;
         end if;

         declare
            Input_Char : constant Character_Type := Input (Index);
         begin
            Index := Index + 1;

            case Input_Char is
               when '0' .. '9' | 'A' .. 'Z' | '_' | 'a' .. 'z' => goto State_69;

            when others =>

               goto Stop;
            end case;
         end;


      <<Stop>>
      --  We end up here as soon as the currently analyzed character was not
      --  accepted by any transitions from the current state. Two cases from
      --  there:

      if Match_Index = 0 then
         --  We haven't found a match. Just create an error token and plan to
         --  start a new token at the next character.
         if Index > Self.Input_Last then
            Token := (Rflx_Termination, Index, Index - 1);
            Self.Has_Next := False;
         else
            Token := (Rflx_Lexing_Failure, First_Index, First_Index);
         end if;

      elsif Match_Ignore then
         --  We found a match. It must be ignored: resume lexing to start right
         --  after the matched text.
         First_Index := Match_Index + 1;
         goto Start;

      else
         --  We found a match for which we must emit a token
         Token := (Match_Kind, First_Index, Match_Index);
      end if;

      Self.Last_Token := Token;
      if not Is_Trivia (Token.Kind) then
         Self.Last_Token_Kind := Token.Kind;
      end if;
   end Next_Token;

end Librflxlang.Lexer_State_Machine;
